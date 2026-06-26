import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { RequestHandler } from '@sveltejs/kit';
import { CreatePostSchema } from '$lib/zodTypes';

export const POST: RequestHandler = async ({ request, locals }) => {
	try {
		if (!locals.user)
			throw error(401, 'Unauthorized');

		// Parse and validate form data
		const formData = await request.formData();
		console.log('Form data received:', formData);
		const data = CreatePostSchema.parse({
			title: formData.get('title') as string,
			subjectId: parseInt(formData.get('subjectId') as string),
			content: formData.get('content') as string,
		});

		// Create Post
		const post = await db.post.create({
			data: {
				title: data.title,
				subjectId: data.subjectId,
				content: data.content,
				userId: locals.user.id
			}
		});

		return json({ post }, { status: 201 });
	} catch (err) {
		console.error('Error creating post:', err);
		return json({ error: 'Failed to create post' }, { status: 500 });
	}
};
