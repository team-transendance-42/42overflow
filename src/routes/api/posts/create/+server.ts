import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, locals }) => {
	try {
		if (!locals.user)
			throw error(401, 'Unauthorized');

		const { projectname, subjectId, body } = await request.json();

		if (!projectname || !subjectId || !body) {
			throw error(400, 'Project name, subject, and body are required');
		}

		const post = await db.post.create({
			data: {
				title: projectname,   // form: projectname (labelled "Project Name")
				subjectId: subjectId,
				content: body,        // form: body (labelled "Question")
				userId: locals.user.id
			}
		});

		return json({ post }, { status: 201 });
	} catch (err) {
		console.error('Error creating post:', err);
		return json({ error: 'Failed to create post' }, { status: 500 });
	}
};
