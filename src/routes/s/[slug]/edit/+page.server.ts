import { db } from '$lib/server/db';
import { error, fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { SubjectRole } from '@prisma/client';

export const load: PageServerLoad = async ({ params, locals }) => {
	const { slug } = params;

	const subject = await db.subject.findUnique({
		where: {
			slug,
		},
		select: {
			id: true,
			name: true,
			slug: true,
			description: true,
			memberships: true,
		},
	});

	if (!subject) {
		throw error(404, 'Subject not found');
	}

    const userIsOwner = subject.memberships.some(
		(membership) => membership.userId === locals.user?.id && membership.role === SubjectRole.OWNER
	);

    if (!locals.user || !userIsOwner) {
        throw error(403, 'Forbidden');
    }

	return {
		subject,
	};
};
