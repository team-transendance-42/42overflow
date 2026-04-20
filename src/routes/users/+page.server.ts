import { error } from '@sveltejs/kit';
import { prisma } from '$lib/server/prisma';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ locals }) => {

	const  currentUser = await prisma.user.findUnique({
		where: { id: locals.user?.id },
		select: { role: true }
	});

	const role = currentUser?.role;
	const isStaff = role === 'ADMIN' || role === 'MODERATOR';
	const isAdmin = role === 'ADMIN';

	if (!isStaff) {
		throw error(403, 'Forbidden');
	}

	const users = await prisma.user.findMany({
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

// export const actions: Actions = {
// 	updateRole: async ({ request, locals }) => {
		
// 		const actor = await prisma.user.findUnique({
// 			where: { id: locals.user?.id },
// 			select: { role: true }
// 		});

// 		if (actor?.role !== 'ADMIN') {
// 			throw error(403, 'Forbidden');
// 		}

// 		const formData = await request.formData();
// 		const targetUserId = formData.get('userId');
// 		const newRole = formData.get('newRole');

// 		if (newRole !== 'USER' && newRole !== 'MODERATOR' && newRole !== 'ADMIN') {
// 			throw error(400, 'Invalid role');
// 		}

// 		if (typeof targetUserId !== 'string' || typeof newRole !== 'string') {
// 			throw error(400, 'Invalid form data');
// 		}

// 		const targetUser = await prisma.user.findUnique({
// 			where: { id: targetUserId },
// 			select: { role: true }
// 		});

// 		if (!targetUser) {
// 			throw error(404, 'User not found');
// 		}

// 		if (targetUser.role === 'ADMIN' && newRole !== 'ADMIN') {
// 			const adminCount = await prisma.user.count({
// 				where: { role: 'ADMIN' }
// 			});

// 			if (adminCount <= 1) {
// 				throw error(400, 'Cannot demote the last admin');
// 			}
// 		}

// 		await prisma.user.update({
// 			where: { id: targetUserId },
// 			data: { role: newRole }
// 		});

// 		return { success: true };
// 	}
// };
