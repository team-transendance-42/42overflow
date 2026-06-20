import { json, error, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const POST = async ({ locals, params }: RequestEvent) => {
	try {
		console.log(`${new Date().toISOString()} - Received request to delete post ID: ${params.postId}`);

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

		const post = await db.post.findUnique({
			where: { id: postId }
		});
		if (!post) {
			throw error(404, 'Post not found');
		}

		// Check user's subject membership role
		const memberships = await db.subjectMember.findMany({
			where: {
				subjectId: post.subjectId,
				userId: locals.user.id
			},
			select: { role: true }
		});
		const subjectRole = memberships[0]?.role;

		// Check if the user has permission to delete the post
		if (locals.user.role !== 'ADMIN'
			&& locals.user.role !== 'MODERATOR'
			&& subjectRole !== 'OWNER'
			&& subjectRole !== 'CURATOR')
		{
			// Check if the user owns the post
			if (post.userId !== locals.user.id) {
				throw error(403, 'You can only delete your own posts');
			}
		}

		// (soft-)Delete the post
		await db.post.update({
			where: { id: postId },
			data: {
				title: '[deleted]',
				content: '[deleted]',
				deleted_at: new Date()
			}
		});

		console.log(`${new Date().toISOString()} - Successfully deleted post ${postId}`);

		return json({ success: true, message: 'Post deleted successfully' }, { status: 200 });
	} catch (error) {
		console.error('Error deleting post:', error);
		throw error;
	}
};
