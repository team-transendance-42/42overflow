import { db } from '$lib/server/db';
import type { LayoutServerLoad } from './posts/$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {

	// fetch subject slug from url
	const subjectSlug = url.pathname.split('/')[2];

	if (!locals.user) {
		return {
			user: null,
			userRole: null
		};
	}

	const dbUser = await db.user.findUnique({
		where: { id: locals.user.id, memberships: { some: { subject: { slug: subjectSlug } } } },
		select: {
			role: true,
			memberships: {
				select: {
					role: true,
					subject: {
						select: {
							slug: true
						}
					}
				}
			}
		}
	});

	if (!dbUser) {
		return {
			hasPermission: false
		};
	}

	let hasPermission =
		dbUser.role === 'ADMIN'
		|| dbUser.role === 'MODERATOR'
		|| dbUser.memberships.some((membership) =>
			membership.subject.slug === subjectSlug
			&& (membership.role === 'OWNER' || membership.role === 'CURATOR'));

	return { hasPermission };
};