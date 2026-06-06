import type { PageServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
	if (!locals.user) throw redirect(303, '/login');

	const response = await fetch(`/api/subjects/${params.slug}/members`);

	if (!response.ok) {
		throw error(response.status, 'Failed to load members');
	}

	const { data } = await response.json();

	return {
		members: data
	};
};