import { useContext } from 'react';
import { FleetContext } from '../context/fleetContextDefinition';

export function useFleet() {
  const context = useContext(FleetContext);
  if (!context) {
    throw new Error('useFleet must be used within a FleetProvider');
  }
  return context;
}
