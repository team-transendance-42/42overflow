import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, locals }) => {
	if (!locals.user) throw error(401, 'Unauthorized');

	const myProfile = await db.user.findUnique({
		where: { id: locals.user.id }
	});

	if (!myProfile) throw error(400, 'Profile not found');

	const { projectname, subject, body } = await request.json();

	const subjectData = await db.subject.findUnique({
		where: { name: subject },
		select: { id: true }
	});

	if (!subjectData || !subjectData.id) throw error(400, 'Subject not found');

	const post = await db.post.create({
		data: {
			title: projectname,   // form: projectname (labelled "Project Name")
			subjectId: subjectData.id,
			content: body,        // form: body (labelled "Question")
			userId: myProfile.id
		}
	});

	return json(post, { status: 201 });
};
