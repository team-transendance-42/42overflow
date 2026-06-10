import { json, error, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const POST = async ({ locals, params }: RequestEvent) => {
	try {
		if (!locals.user) {
			throw error(401, 'Unauthorized');
		}

		if (!params.postId) {
			throw error(400, 'Post ID is required');
		}
		const postId = parseInt(params.postId);
		if (isNaN(postId)) {
			throw error(400, 'Invalid Post ID');
		}

		if (!params.commentId) {
			throw error(400, 'Comment ID is required');
		}
		const commentId = parseInt(params.commentId);
		if (isNaN(commentId)) {
			throw error(400, 'Invalid Comment ID');
		}

		// Check if user has already liked the comment
		const existingLike = await db.like.findFirst({
			where: {
				userId: locals.user.id,
				commentId: commentId
			}
		});

		if (existingLike) {
			throw error(400, 'User has already liked this comment');
		}

		// Create like
		await db.like.create({
			data: {
				userId: locals.user.id,
				commentId: commentId
			}
		});

		return json({ success: true, message: 'User: ' + locals.user.id + ' liked comment: ' + commentId }, { status: 200 });
	} catch (error) {
		console.error('Error liking comment:', error);
		throw error;
	}
};
