import { json, error } from "@sveltejs/kit";
import { db } from '$lib/server/db';
import type { RequestHandler } from "@sveltejs/kit";
import { SubjectRole } from "@prisma/client";
import { SubjectDescriptionSchema } from "$lib/zodTypes";

export const POST: RequestHandler = async ({ request, locals, params }) => {
	try {
		const { slug } = params;

		if (!locals.user) {
			throw error(401, "Unauthorized");
		}

		if (!slug) {
			throw error(400, "Slug is required");
		}

		// Parse and validate form data
		const formData = await request.formData();
		console.log('Form data received:', formData);
		const data = SubjectDescriptionSchema.parse({
			description: formData.get('description') as string,
		});

		const subject = await db.subject.findUnique({
			where: { slug: slug },
			include: { memberships: true }
		});

		if (!subject) {
			throw error(404, "Subject not found");
		}

		// Check if the authorized user is the owner of the subject
		const userIsOwner = subject.memberships.some(
			(membership) => membership.userId === locals.user?.id && membership.role === SubjectRole.OWNER
		);

		if (!userIsOwner) {
			throw error(403, "Forbidden");
		}

		const updatedSubject = await db.subject.update({
			where: { slug: slug },
			data: { description: data.description },
		});

		return json(updatedSubject, { status: 201 });
	} catch (err) {
		console.error('Error updating subject:', err);
		return json({ error: 'Failed to update subject' }, { status: 500 });
	}
};