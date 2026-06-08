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
		include: {
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

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const { slug } = params;
		const data = await request.formData();
		const description = data.get('description');

		if (typeof description !== 'string') {
			return fail(400, { description, error: 'Description must be a string' });
		}

		const response = await fetch(`/api/subjects/${slug}/edit`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ description }),
		});

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, { description, error: errorData.message });
		}

		// throw redirect(303, `/s/${slug}`);
	},
};
