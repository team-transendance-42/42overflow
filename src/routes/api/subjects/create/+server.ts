import { json, error } from "@sveltejs/kit";
import { db } from '$lib/server/db';
import type { RequestHandler } from "@sveltejs/kit";
import { SubjectRole } from "@prisma/client";
import { CreateSubjectSchema } from "$lib/zodTypes";

const slugify = (name: string) => {
	return name
		.trim()
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric characters with hyphens
		.replace(/^-+|-+$/g, ''); // Remove leading and trailing hyphens
}

export const POST: RequestHandler = async ({ request, locals }) => {
	try {
		if (!locals.user)
			throw error(401, 'Unauthorized');

		// Parse and validate form data
		const formData = await request.formData();
		console.log('Form data received:', formData);
		const data = CreateSubjectSchema.parse({
			name: formData.get('name') as string,
			description: formData.get('description') as string,
		});

		// Create Subject
		const subject = await db.subject.create({
			data: {
				name: data.name,
				slug: slugify(data.name),
				description: data.description || null,
				memberships: {
					create: {
						userId: locals.user.id,
						role: SubjectRole.OWNER
					}
				}
			}
		});

		return json({ subject }, { status: 201 });
	} catch (err) {
		console.error('Error creating subject:', err);
		return json({ error: 'Failed to create subject' }, { status: 500 });
	}
};
