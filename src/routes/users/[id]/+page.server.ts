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

async function requireStaff(actorId: string | undefined) {
	if (!actorId) {
		throw error(403, 'Forbidden');
	}
	
	const actor = await prisma.user.findUnique({
		where: { id: actorId },
		select: { role: true }
	});

	if (actor?.role !== 'ADMIN' && actor?.role !== 'MODERATOR') {
		throw error(403, 'Forbidden');
	}

	return actor.role;
}

export const load: PageServerLoad = async ({ locals, params }) => {
	const role = await requireStaff(locals.user?.id);

	const isAdmin = role === 'ADMIN';

	const user = await prisma.user.findUnique({
		where: { id: params.id },
		select: isAdmin ? {
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
		} : {
			id: true,
			name: true,
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

		await prisma.follow.deleteMany({
			where: {
				OR: [
					{ followerId: params.id },
					{ followingId: params.id }
				]
			}
		});

		await prisma.user.update({
			where: { id: params.id },
			data: { deleted_at: new Date(),
				name: "deleted_user#" + params.id,
				email: "deleted_user#" + params.id,
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
