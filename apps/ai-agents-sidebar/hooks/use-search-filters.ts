import { useState } from 'react';

export function useSearchFilters() {
  const [filters, setFilters] = useState({});

  const updateFilter = (key: string, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return { filters, updateFilter };
}
