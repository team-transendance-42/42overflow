import { error, redirect } from '@sveltejs/kit';
import { SubjectRole } from '@prisma/client';
import { prisma } from '$lib/server/prisma';
import { getSubjectRole } from '$lib/server/subject-access';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
	if (!locals.user) throw redirect(303, '/login');

	const slug = params.slug;
	if (!slug) throw error(400, 'Slug is required');

	const role = await getSubjectRole(slug, locals.user.id);
	if (role !== SubjectRole.OWNER) {
		throw error(403, 'Forbidden');
	}

	const subject = await prisma.subject.findUnique({
		where: { slug },
		select: {
			id: true,
			name: true,
			slug: true,
			deleted_at: true
		}
	});

	if (!subject || subject.deleted_at) {
		throw error(404, 'Subject not found');
	}

	return {
		subject: {
			name: subject.name,
			slug: subject.slug
		},
		currentUserId: locals.user.id
	};
};