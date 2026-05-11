import { prisma } from '$lib/server/prisma';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {

	if (!locals.user) {
		return {
			user: null,
			userRole: null
		};
	}

	const dbUser = await prisma.user.findUnique({
		where: {
			id: locals.user.id
		},
		select: {
			role: true
		}
	});

	return {
		user: {
			id: locals.user.id
		},
		userRole: dbUser?.role ?? null
	};
};