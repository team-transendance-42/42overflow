import { redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) throw redirect(303, '/login');

	const user = await db.user.findUnique({
		where: { id: locals.user.id },
		include: {
			followers: {
				include: { following: true, }
			}
		}
	});

	return { user };
};
