import { json, error, type RequestEvent } from '@sveltejs/kit';
import { PostSchema } from '$lib/zodTypes.js';
import { db } from '$lib/server/db';
import { z } from 'zod';

export const POST = async ({ locals, request, params }: RequestEvent) => {
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

		// Get the post to verify ownership
		const post = await db.post.findUnique({
			where: { id: postId }
		});

		if (!post) {
			throw error(404, 'Post not found');
		}

		// Check if the user owns the post
		if (post.userId !== locals.user.id) {
			throw error(403, 'You can only edit your own posts');
		}

		const formData = await request.formData();

		// Extract form fields and convert types
		const postData = {
			postId: postId,
			title: formData.get('title') as string,
			content: formData.get('content') as string,
		}

		const data = PostSchema.parse(postData);

		// Edit post
		const editedPost = await db.post.update({
			where: { id: postId },
			data: {
				title: data.title,
				content: data.content
			}
		});

		return json({ post: editedPost }, { status: 201 });
	} catch (error) {
		console.error('Error editing post:', error);
		if (error instanceof z.ZodError) {
			return json({
				error: 'Invalid input data',
				details: error.issues.map(e => ({
					field: e.path.join('.'),
					message: e.message
				}))
			}, { status: 400 });
		}
		return json({ error: 'Failed to edit post' }, { status: 500 });
	}
};
