import { json, error } from "@sveltejs/kit";
import { prisma } from '$lib/server/prisma';
import type { RequestHandler } from "@sveltejs/kit";
import { SubjectRole } from "@prisma/client";

const slugify = (name: string) => {
	return name
		.trim()
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric characters with hyphens
		.replace(/^-+|-+$/g, ''); // Remove leading and trailing hyphens
}

export const POST: RequestHandler = async ({ request, locals }) => {
	const { name, description } = await request.json();

	if (!locals.user) {
		throw error(401, "Unauthorized");
	}

	if (!name || typeof name !== "string") {
		throw error(400, "Name is required and must be a string");
	}

	const slug = slugify(name);

	const subject = await prisma.subject.create({
		data: {
			name,
			slug,
			description: description || null,
			memberships: {
				create: {
					userId: locals.user.id,
					role: SubjectRole.OWNER
				}
			}
		}
	});

	return json(subject, { status: 201 });
};
