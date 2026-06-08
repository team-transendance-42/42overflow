import { SubjectRole } from "@prisma/client";
import {json, error} from "@sveltejs/kit";
import { db } from '$lib/server/db';
import type {RequestHandler} from "@sveltejs/kit";
import { url } from "inspector";
import { boolean, date } from "better-auth";

export const GET: RequestHandler = async ({ url, locals }) => {
	const isLoggedIn = Boolean(locals.user);

	const page = Math.max(1, Number(url.searchParams.get('page') ?? 1));
	const limit = Math.min(50, Number(url.searchParams.get('limit') ?? 10));
	const skip = (page - 1) * limit;

	const [subjects, total] = await Promise.all([
		db.subject.findMany({
			where: { deleted_at: null },
			orderBy: { created_at: 'desc' },
			skip,
			take: limit,
			select: {
				id: true,
				name: true,
				slug: true,
				description: true,
				created_at: true,
				_count: {
					select: {
						memberships: true,
						posts: true
					}
				},
				memberships: locals.user ? {
					where: { userId: locals.user.id },
					select: { id: true, role: true },
					take: 1
				} : false
			}
		}),
		db.subject.count({ where: { deleted_at: null } })
	]);

	const data = subjects.map(subject => ({
		id: subject.id,
		name: subject.name,
		slug: subject.slug,
		description: subject.description,
		created_at: subject.created_at,
		memberCount: subject._count.memberships,
		postCount: subject._count.posts,
		isMember: isLoggedIn ? subject.memberships.length > 0 : false,
		isOwner: isLoggedIn ? subject.memberships.some(m => m.role === SubjectRole.OWNER) : false
	}));

	return json({
		data,
		isLoggedIn,
		page,
		limit,
		total,
		totalPages: Math.ceil(total / limit)
	});
};