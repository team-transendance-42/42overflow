import { json, error, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { broadcast } from '$lib/server/sse';

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

		const likeCount = await db.like.count({
			where: { commentId }
		});

		const userLiked = await db.like.findFirst({
			where: {
				commentId,
				userId: locals.user.id
			}
		});

		broadcast({
			type: 'like-update',
			commentId,
			likeCount,
			userLiked: !!userLiked
		});

		return json({ success: true, message: 'User: ' + locals.user.id + ' liked comment: ' + commentId }, { status: 200 });
	} catch (error) {
		console.error('Error liking comment:', error);
		throw error;
	}
};
