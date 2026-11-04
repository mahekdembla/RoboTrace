"""RoboTrace 3D — Human Annotation Manager.

Manages the human-in-the-loop review workflow for AgentGuard detected errors:
1. Retrieve pending errors awaiting review.
2. Retrieve error details and evidence.
3. Accept AgentGuard prediction (review_status = CONFIRMED).
4. Reject prediction (review_status = REJECTED).
5. Correct error category (review_status = CORRECTED).
6. Save reviewer feedback and timestamped notes.
7. Track review lifecycle status.
8. Retrieve annotations scoped by mission or error.

Guarantees:
- Original AgentGuard prediction in the Error table is NEVER overwritten or mutated.
- Human corrections are stored in distinct Annotation records linked by error_id.
- Annotations are strictly for human evaluation and auditing; no automatic model re-training is performed.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from agentguard.agent_guard import AgentGuard, DetectedError
from agentguard.error_classifier import ErrorCategory
from database.db import get_db_session
from database.models import Annotation

logger = logging.getLogger("robotrace.annotations")


@dataclass
class AnnotationRecord:
    """Human review record for an error."""
    id: int
    error_id: int
    original_suggested_category: str
    corrected_category: str
    review_status: str  # CONFIRMED, REJECTED, CORRECTED
    annotator: str
    notes: Optional[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "error_id": self.error_id,
            "original_suggested_category": self.original_suggested_category,
            "corrected_category": self.corrected_category,
            "review_status": self.review_status,
            "annotator": self.annotator,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AnnotationManager:
    """Manages human review lifecycle for detected errors."""

    def __init__(self, agent_guard: AgentGuard):
        self.agent_guard = agent_guard
        self._next_annotation_id: int = 1
        self._annotations: Dict[int, AnnotationRecord] = {}  # id -> record
        self._error_annotations: Dict[int, List[int]] = {}   # error_id -> list of annotation_ids

    # -----------------------------------------------------------------------
    # Query Operations
    # -----------------------------------------------------------------------

    def get_pending_errors(self, mission_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve errors that do not have any submitted annotations yet."""
        all_errors = self.agent_guard.get_errors(mission_id)
        pending = []
        for err in all_errors:
            if err.id not in self._error_annotations or not self._error_annotations[err.id]:
                pending.append(err.to_dict())
        return pending

    def get_error_details(self, error_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve full details of an error and all associated human annotations."""
        err = self.agent_guard.get_error_by_id(error_id)
        if err is None:
            return None

        details = err.to_dict()
        ann_ids = self._error_annotations.get(error_id, [])
        details["annotations"] = [self._annotations[aid].to_dict() for aid in ann_ids if aid in self._annotations]
        details["review_status"] = details["annotations"][-1]["review_status"] if details["annotations"] else "PENDING_REVIEW"
        return details

    def get_annotations(
        self,
        mission_id: Optional[int] = None,
        error_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve submitted annotations filtered by mission or error."""
        records = list(self._annotations.values())
        if error_id is not None:
            records = [r for r in records if r.error_id == error_id]

        if mission_id is not None:
            # Match via error mission_id
            matched_error_ids = {e.id for e in self.agent_guard.get_errors(mission_id)}
            records = [r for r in records if r.error_id in matched_error_ids]

        return [r.to_dict() for r in records]

    # -----------------------------------------------------------------------
    # Review Actions (Accept, Reject, Correct)
    # -----------------------------------------------------------------------

    def accept_prediction(
        self,
        error_id: int,
        annotator: str,
        notes: Optional[str] = None,
        persist_db: bool = True,
    ) -> AnnotationRecord:
        """Human confirms that AgentGuard's suggested category is accurate."""
        err = self.agent_guard.get_error_by_id(error_id)
        if err is None:
            raise ValueError(f"Error with ID {error_id} does not exist.")

        return self._create_annotation(
            error=err,
            corrected_category=err.suggested_category,
            review_status="CONFIRMED",
            annotator=annotator,
            notes=notes or "AgentGuard category confirmed by human reviewer.",
            persist_db=persist_db,
        )

    def reject_prediction(
        self,
        error_id: int,
        annotator: str,
        notes: Optional[str] = None,
        persist_db: bool = True,
    ) -> AnnotationRecord:
        """Human rejects AgentGuard's classification without supplying an alternate."""
        err = self.agent_guard.get_error_by_id(error_id)
        if err is None:
            raise ValueError(f"Error with ID {error_id} does not exist.")

        return self._create_annotation(
            error=err,
            corrected_category="REJECTED",
            review_status="REJECTED",
            annotator=annotator,
            notes=notes or "Classification rejected by reviewer.",
            persist_db=persist_db,
        )

    def correct_category(
        self,
        error_id: int,
        corrected_category: str,
        annotator: str,
        notes: Optional[str] = None,
        persist_db: bool = True,
    ) -> AnnotationRecord:
        """Human overrides and supplies the corrected error category.

        Never alters the original error.suggested_category.
        """
        err = self.agent_guard.get_error_by_id(error_id)
        if err is None:
            raise ValueError(f"Error with ID {error_id} does not exist.")

        # Validate category
        valid_cats = {c.value for c in ErrorCategory}
        clean_cat = corrected_category.upper()
        if clean_cat not in valid_cats:
            raise ValueError(f"Invalid corrected category '{corrected_category}'. Allowed: {sorted(valid_cats)}")

        return self._create_annotation(
            error=err,
            corrected_category=clean_cat,
            review_status="CORRECTED",
            annotator=annotator,
            notes=notes,
            persist_db=persist_db,
        )

    def _create_annotation(
        self,
        error: DetectedError,
        corrected_category: str,
        review_status: str,
        annotator: str,
        notes: Optional[str],
        persist_db: bool = True,
    ) -> AnnotationRecord:
        """Internal helper to create, register, and persist an annotation record."""
        ann_id = self._next_annotation_id
        self._next_annotation_id += 1
        now_iso = datetime.now(timezone.utc).isoformat()

        record = AnnotationRecord(
            id=ann_id,
            error_id=error.id,
            original_suggested_category=error.suggested_category,
            corrected_category=corrected_category,
            review_status=review_status,
            annotator=annotator,
            notes=notes,
            created_at=now_iso,
            updated_at=now_iso,
        )

        self._annotations[ann_id] = record
        self._error_annotations.setdefault(error.id, []).append(ann_id)

        logger.info(
            "Created annotation %d for error %d: status=%s, corrected=%s, by=%s (original '%s' preserved)",
            ann_id, error.id, review_status, corrected_category, annotator, error.suggested_category,
        )

        if persist_db:
            try:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop is not None and loop.is_running():
                    loop.create_task(self._persist_to_sqlite(record))
                else:
                    asyncio.run(self._persist_to_sqlite(record))
            except Exception as exc:
                logger.warning("AnnotationManager persistence error: %s", exc)

        return record

    async def _persist_to_sqlite(self, record: AnnotationRecord) -> None:
        """Persist annotation row into SQLite."""
        try:
            async with get_db_session() as session:
                ann = Annotation(
                    id=record.id,
                    error_id=record.error_id,
                    original_suggested_category=record.original_suggested_category,
                    corrected_category=record.corrected_category,
                    review_status=record.review_status,
                    annotator=record.annotator,
                    notes=record.notes,
                )
                await session.merge(ann)
        except Exception as exc:
            logger.warning("Failed to persist annotation to SQLite: %s", exc)

