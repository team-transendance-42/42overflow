import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { prisma } from '$lib/server/prisma';

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
}

export const load: PageServerLoad = async ({ locals, params }) => {
	await requireStaff(locals.user?.id);
	
	const user = await prisma.user.findUnique({
		where: { id: params.id },
		select: {
			id: true,
		}
	});
	
	return { user };
};