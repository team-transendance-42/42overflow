import type { RequestHandler } from '@sveltejs/kit';
import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { SubjectRole } from '@prisma/client';
import { getSubjectRole } from '$lib/server/subject-access';

export const GET: RequestHandler = async ({ params, locals }) => {
	if (!locals.user) throw error(401, 'Unauthorized');

	const slug = params.slug;
	if (!slug) throw error(400, 'Slug is required');

	const currentRole = await getSubjectRole(slug, locals.user.id);
	if (currentRole !== SubjectRole.OWNER && currentRole !== SubjectRole.CURATOR) {
		throw error(403, 'Forbidden');
	}

	const subject = await db.subject.findUnique({
		where: { slug },
		select: { id: true, deleted_at: true }
	});

	if (!subject || subject.deleted_at) {
		throw error(404, 'Subject not found');
	}

	const members = await db.subjectMember.findMany({
		where: { subjectId: subject.id },
		orderBy: [{ role: 'asc' }, { joined_at: 'asc' }],
		select: {
			userId: true,
			role: true,
			joined_at: true,
			user: {
				select: {
					id: true,
					name: true,
					image: true
				}
			}
		}
	});

	return json({ data: members });
};

export const PATCH: RequestHandler = async ({ params, locals, request }) => {
	if (!locals.user) throw error(401, 'Unauthorized');

	const slug = params.slug;
	if (!slug) throw error(400, 'Slug is required');

	const currentRole = await getSubjectRole(slug, locals.user.id);
	if (currentRole !== SubjectRole.OWNER) {
		throw error(403, 'Forbidden');
	}

	const body = await request.json();
	const targetUserId = typeof body?.targetUserId === 'string' ? body.targetUserId : null;
	const nextRole = body?.role;

	if (!targetUserId) {
		throw error(400, 'targetUserId is required');
	}

	if (nextRole !== SubjectRole.MEMBER && nextRole !== SubjectRole.CURATOR && nextRole !== SubjectRole.OWNER) {
		throw error(400, 'role must be MEMBER, CURATOR or OWNER');
	}

	if (targetUserId === locals.user.id) {
		throw error(400, 'You cannot change your own role');
	}

	const subject = await db.subject.findUnique({
		where: { slug },
		select: { id: true, deleted_at: true }
	});

	if (!subject || subject.deleted_at) {
		throw error(404, 'Subject not found');
	}

	const targetMembership = await db.subjectMember.findUnique({
		where: {
			userId_subjectId: {
				userId: targetUserId,
				subjectId: subject.id
			}
		},
		select: { role: true }
	});

	if (!targetMembership) {
		throw error(404, 'Subject member not found');
	}

	// if (targetMembership.role === SubjectRole.OWNER) {
	// 	throw error(400, 'Owner role cannot be changed here');
	// }

	const updated = await db.subjectMember.update({
		where: {
			userId_subjectId: {
				userId: targetUserId,
				subjectId: subject.id
			}
		},
		data: { role: nextRole },
		select: {
			userId: true,
			role: true,
			joined_at: true,
			user: {
				select: {
					id: true,
					name: true,
					image: true
				}
			}
		}
	});

	return json({ data: updated });
};