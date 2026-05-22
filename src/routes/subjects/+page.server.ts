import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
  const page = url.searchParams.get('page') ?? '1';
  const limit = url.searchParams.get('limit') ?? '10';

  const res = await fetch(`/api/subjects?page=${page}&limit=${limit}`);
  
  if (!res.ok) {
    throw new Error('Failed to fetch subjects');
  }

  const { data: subjects, total, page: currentPage, totalPages, isLoggedIn } = await res.json();

  return {
    subjects,
    total,
    currentPage,
    totalPages,
	isLoggedIn
  };
};