import type { PageServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';
import { getSubjectRole } from '$lib/server/subject-access';
import { SubjectRole } from '@prisma/client';

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
	if (!locals.user) throw redirect(303, '/login');

	const role = await getSubjectRole(params.slug, locals.user.id);
		if (role !== SubjectRole.OWNER) {
			throw error(403, 'Forbidden');
		}

	const response = await fetch(`/api/subjects/${params.slug}/members`);

	if (!response.ok) {
		throw error(response.status, 'Failed to load members');
	}

	const { data } = await response.json();

	return {
		members: data
	};
};