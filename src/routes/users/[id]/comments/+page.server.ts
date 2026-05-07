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
	
	const comments = await prisma.comment.findMany({
		where: { userId: params.id },
		orderBy: { created_at: 'desc' }
	});

	return { user, comments };
};

export const actions = {
	deleteComment: async ({ request, locals }) => {
		await requireStaff(locals.user?.id);

		const formData = await request.formData();
		const commentId = formData.get('commentId') as string;

		await prisma.comment.update({
			where: { id: Number(commentId) },
			data: { deleted_at: new Date(), content: '[deleted by staff]' }
		});

		return { success: true, message: 'Comment deleted successfully' };
	}
};