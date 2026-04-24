import { error, fail } from '@sveltejs/kit';
import { prisma } from '$lib/server/prisma';
import type { Actions, PageServerLoad } from './$types';
import type { Role } from '@prisma/client';

function splitName(name: string | null) {
	if (!name) {
		return { firstName: '', lastName: '' };
	}

	const trimmed = name.trim();
	if (!trimmed) {
		return { firstName: '', lastName: '' };
	}

	const [firstName, ...rest] = trimmed.split(/\s+/);
	return {
		firstName,
		lastName: rest.join(' ')
	};
}

async function requireAdmin(actorId: string | undefined) {
	if (!actorId) {
		throw error(403, 'Forbidden');
	}

	const actor = await prisma.user.findUnique({
		where: { id: actorId },
		select: { role: true }
	});

	if (actor?.role !== 'ADMIN') {
		throw error(403, 'Forbidden');
	}
}

export const load: PageServerLoad = async ({ locals, params }) => {
	await requireAdmin(locals.user?.id);

	const user = await prisma.user.findUnique({
		where: { id: params.id },
		select: {
			id: true,
			name: true,
			first_name: true,
			last_name: true,
			email: true,
			image: true,
			role: true,
			createdAt: true,
			updatedAt: true,
			biography: true,
			interests: true
		}
	});

	if (!user) {
		throw error(404, 'User not found');
	}

	const posts = await prisma.post.findMany({
		where: { userId: user.id },
		select: {
			id: true,
			title: true,
			created_at: true,
			deleted_at: true
		},
		orderBy: { created_at: 'desc' }
	});

	return {
		user,
		posts
	};
};

export const actions: Actions = {
	updateUserCore: async ({ request, locals, params }) => {
		await requireAdmin(locals.user?.id);

		const formData = await request.formData();
		const username = formData.get('username');
		const firstName = formData.get('firstName');
		const lastName = formData.get('lastName');
		const email = formData.get('email');
		const image = formData.get('image');
		const role = formData.get('role');
		const biography = formData.get('biography');
		const interests = formData.get('interests');

		if (
			typeof username !== 'string' ||
			typeof firstName !== 'string' ||
			typeof lastName !== 'string' ||
			typeof email !== 'string' ||
			typeof image !== 'string' ||
			typeof role !== 'string' ||
			typeof biography !== 'string' ||
			typeof interests !== 'string'
		) {
			return fail(400, { message: 'Invalid form data' });
		}

		const normalizedRole = role as Role;
		if (!['USER', 'MODERATOR', 'ADMIN'].includes(normalizedRole)) {
			return fail(400, { message: 'Invalid role' });
		}

		const normalizedEmail = email.trim().toLowerCase();
		if (!normalizedEmail) {
			return fail(400, { message: 'Email is required' });
		}

		const targetUser = await prisma.user.findUnique({
			where: { id: params.id },
			select: { role: true }
		});

		if (!targetUser) {
			throw error(404, 'User not found');
		}

		if (targetUser.role === 'ADMIN' && normalizedRole !== 'ADMIN') {
			const adminCount = await prisma.user.count({ where: { role: 'ADMIN' } });
			if (adminCount <= 1) {
				return fail(400, { message: 'Cannot demote the last admin' });
			}
		}

		const existingEmail = await prisma.user.findFirst({
			where: {
				email: normalizedEmail,
				NOT: { id: params.id }
			},
			select: { id: true }
		});

		if (existingEmail) {
			return fail(400, { message: 'Email is already in use' });
		}

		const existingUsername = await prisma.user.findFirst({
			where: {
				name: username.trim(),
				NOT: { id: params.id }
			},
			select: { id: true }
		});

		if (existingUsername) {
			return fail(400, { message: 'Username is already in use' });
		}

		await prisma.user.update({
			where: { id: params.id },
			data: {
				name: username || null,
				email: normalizedEmail,
				image: image.trim() || null,
				role: normalizedRole,
				biography: biography || null,
				interests: interests || null,
				first_name: firstName.trim() || null,
				last_name: lastName.trim() || null
			}
		});

		return { success: true, message: 'User details updated' };
	},

	// updateProfile: async ({ request, locals, params }) => {
	// 	await requireAdmin(locals.user?.id);

	// 	const formData = await request.formData();
	// 	const login = formData.get('login');
	// 	const biography = formData.get('biography');

	// 	if (
	// 		typeof login !== 'string' ||
	// 		typeof biography !== 'string'
	// 	) {
	// 		return fail(400, { message: 'Invalid form data' });
	// 	}

	// 	const userExists = await prisma.user.findUnique({
	// 		where: { id: params.id },
	// 		select: { id: true }
	// 	});

	// 	if (!userExists) {
	// 		throw error(404, 'User not found');
	// 	}

	// 	const normalizedLogin = login.trim();
	// 	if (normalizedLogin) {
	// 		const loginInUse = await prisma.user.findFirst({
	// 			where: {
	// 				name: normalizedLogin,
	// 				NOT: { id: params.id }
	// 			},
	// 			select: { id: true }
	// 		});

	// 		if (loginInUse) {
	// 			return fail(400, { message: 'Intra profile is already in use' });
	// 		}
	// 	}

	// 	await prisma.user.upsert({
	// 		where: { id: params.id },
	// 		update: {
	// 			name: normalizedLogin || null,
	// 			biography: biography.trim() || null
	// 		}
	// 	});

	// 	return { success: true, message: 'Profile details updated' };
	// },

	deleteUser: async ({ locals, params }) => {
		await requireAdmin(locals.user?.id);

		const targetUser = await prisma.user.findUnique({
			where: { id: params.id },
			select: { role: true }
		});

		if (!targetUser) {
			throw error(404, 'User not found');
		}

		if (targetUser.role === 'ADMIN') {
			const adminCount = await prisma.user.count({ where: { role: 'ADMIN' } });
			if (adminCount <= 1) {
				return fail(400, { message: 'Cannot delete the last admin' });
			}
		}

		await prisma.user.update({
			where: { id: params.id },
			data: { deleted_at: new Date(),
				name: "deleted",
				email: "deleted",
				image: null,
				role: 'USER',
				biography: null,
				interests: null,
				first_name: null,
				last_name: null
			}
		});

		return { success: true, message: 'User deleted' };
	}
};
