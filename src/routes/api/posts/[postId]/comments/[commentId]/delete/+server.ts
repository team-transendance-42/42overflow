import { json, error, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const POST = async ({ locals, params }: RequestEvent) => {
	try {
		console.log(`${new Date().toISOString()} - Received request to delete comment on post ID: ${params.postId}`);

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

		// Get the comment to verify ownership
		const comment = await db.comment.findUnique({
			where: { id: commentId }
		});

		if (!comment) {
			throw error(404, 'Comment not found');
		}

		// Check if the user owns the comment
		if (comment.userId !== locals.user.id) {
			throw error(403, 'You can only delete your own comments');
		}

		// (soft-)Delete the comment
		await db.comment.update({
			where: { id: commentId },
			data: {
				content: '[deleted]',
				image: null,
				deleted_at: new Date()
			}
		});

		console.log(`${new Date().toISOString()} - Successfully deleted comment ${commentId}`);

		return json({ success: true, message: 'Comment deleted successfully' }, { status: 200 });
	} catch (error) {
		console.error('Error deleting comment:', error);
		throw error;
	}
};
