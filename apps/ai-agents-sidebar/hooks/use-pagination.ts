import { useState } from 'react';

export function usePagination() {
  const [currentPage, setCurrentPage] = useState(1);

  const goToPage = (page: number) => {
    setCurrentPage(page);
  };

  return { currentPage, goToPage };
}
