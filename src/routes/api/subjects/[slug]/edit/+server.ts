import { json, error } from "@sveltejs/kit";
import { db } from '$lib/server/db';
import type { RequestHandler } from "@sveltejs/kit";
import { SubjectRole } from "@prisma/client";
export const PATCH: RequestHandler = async ({ request, locals, params }) => {
	
	const { description } = await request.json();
	const { slug } = params;

	if (!locals.user) {
		throw error(401, "Unauthorized");
	}

	if (typeof description !== "string") {
		throw error(400, "Description must be a string");
	}

	if (!slug) {
		throw error(400, "Slug is required");
	}

	const subject = await db.subject.findUnique({
		where: {
			slug: slug,
		},
		include: {
			memberships: true,
		}
	});

	if (!subject) {
		throw error(404, "Subject not found");
	}

	const userIsOwner = subject.memberships.some(
		(membership) => membership.userId === locals.user?.id && membership.role === SubjectRole.OWNER
	);

	if (!userIsOwner) {
		throw error(403, "Forbidden");
	}

	const updatedSubject = await db.subject.update({
		where: {
			slug: slug,
		},
		data: {
			description: description,
		},
	});

	return json(updatedSubject, { status: 200 });
};