import { error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	
	if (!locals.user) {
		throw error(403, 'Forbidden');
	}

	const  currentUser = await db.user.findUnique({
		where: { id: locals.user?.id },
		select: { role: true }
	});

	const role = currentUser?.role;
	const isStaff = role === 'ADMIN' || role === 'MODERATOR';
	const isAdmin = role === 'ADMIN';

	if (!isStaff) {
		throw error(403, 'Forbidden');
	}

	const users = await db.user.findMany({
		where: { deleted_at: null },
		select: isAdmin ? {
			id: true,
			name: true,
			email: true,
			role: true,
			image: true,
			createdAt: true
		} : {
			id: true,
			name: true,
			role: true,
			image: true,
			createdAt: true
		},
		orderBy: {
			createdAt: 'desc'
		}
	});

	return { users, canViewEmail: isAdmin, canManageRoles: isAdmin };
};

