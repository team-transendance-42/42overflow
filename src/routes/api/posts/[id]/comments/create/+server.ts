import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, locals, params }) => {
	if (!locals.user) {
		throw error(401, 'Unauthorized');
	}

	if (!params.id) {
		throw error(400, 'Post ID is required');
	}
	const postId = parseInt(params.id);

	if (isNaN(postId)) {
		throw error(400, 'Invalid Post ID');
	}

	const { parentId, body } = await request.json();

	const comment = await db.comment.create({
		data: {
			content: `${body}`,
			parentId: parentId,
			postId: postId,
			userId: locals.user.id,
		}
	});

	return json(comment, { status: 201 });
};
