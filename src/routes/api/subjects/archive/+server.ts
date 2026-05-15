import {json, error} from "@sveltejs/kit";
import {prisma} from '$lib/server/prisma';
import type {RequestHandler} from "@sveltejs/kit";

export const POST: RequestHandler = async ({ request, locals }) => {
	const { slug } = await request.json();

	if (!locals.user) {
		throw error(401, "Unauthorized");
	}

	if (!slug || typeof slug !== "string") {
		throw error(400, "Slug is required and must be a string");
	}

	const owner = await prisma.subjectMember.findFirst({
		where: {
				userId: locals.user.id,
				subject: { slug }
		}
	});

	if (!owner || owner.role !== "OWNER") {
		throw error(403, "Forbidden");
	}

	const subject = await prisma.subject.update({
		where: { slug: slug},
		data: { deleted_at: new Date() }
	});

	return json(subject, { status: 200 });
};
