import type { RequestHandler } from '@sveltejs/kit';
import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const POST: RequestHandler = async ({ request, locals, params }) => {
	if (!locals.user) throw error(401, 'Unauthorized');

	const { slug } = params;
	if (!slug) throw error(400, 'Slug is required');

	const {title, content} = await request.json();
	if (!title || typeof title !== 'string') throw error(400, 'Title is required');
	if (!content || typeof content !== 'string') throw error(400, 'Content is required');

	const subject = await db.subject.findUnique({
		where: { slug },
		select: { id: true, deleted_at: true }
	});

	if (!subject || subject.deleted_at) throw error(404, 'Subject not found');

	const post = await db.post.create({
		data: {
			title,
			content,
			userId: locals.user.id,
			subjectId: subject.id
		},
	})

	return json(post, { status: 201 });
};