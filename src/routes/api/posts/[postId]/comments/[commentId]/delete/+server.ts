import { json, error, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { broadcast } from '$lib/server/sse';

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

		const comment = await db.comment.findUnique({
			where: { id: commentId },
			include: {
				post: true,
				select: { subjectId: true },
			}
		});
		if (!comment) {
			throw error(404, 'Comment not found');
		}

		// Check user's subject membership role
		const memberships = await db.subjectMember.findMany({
			where: {
				subjectId: comment.post.subjectId,
				userId: locals.user.id
			},
			select: { role: true }
		});
		const subjectRole = memberships[0]?.role;

		// Check if the user has permission to delete the comment
		if (locals.user.role !== 'ADMIN'
			&& locals.user.role !== 'MODERATOR'
			&& subjectRole !== 'OWNER'
			&& subjectRole !== 'CURATOR')
		{
			// Check if the user owns the comment
			if (comment.userId !== locals.user.id) {
				throw error(403, 'You can only delete your own comments');
			}
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

		// re-fetch with relations if needed
        const fullComment = await db.comment.findUnique({
            where: { id: commentId },
            include: {
                user: true,
                likes: true
            }
        });

		broadcast({
			type: 'comment-update',
			comment: {
                ...fullComment,
                likeCount: fullComment.likes.length
            }
		});

		console.log(`${new Date().toISOString()} - Successfully deleted comment ${commentId}`);

		return json({ success: true, message: 'Comment deleted successfully' }, { status: 200 });
	} catch (error) {
		console.error('Error deleting comment:', error);
		throw error;
	}
};
