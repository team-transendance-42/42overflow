import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const users = await db.user.findMany({
		select: {
			id: true,
			name: true,
			email: true,
			role: true,
			image: true,
			createdAt: true
		},
		orderBy: {
			createdAt: 'desc'
		}
	});

	return { users };
};
