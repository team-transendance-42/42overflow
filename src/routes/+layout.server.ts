import { db } from '$lib/server/db';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {

	if (!locals.user) {
		return {
			user: null,
			userRole: null
		};
	}

	const dbUser = await db.user.findUnique({
		where: {
			id: locals.user.id
		},
		select: {
			name: true,
			image: true,
			role: true,
			memberships: {
				select: {
					subject: {
						select: {
							name: true,
							slug: true
						}
					}
				}
			}
		}
	});

    return {
        user: {
            id: locals.user.id,
			name: dbUser?.name,
			image: dbUser?.image,
			memberships: dbUser?.memberships ?? []
        },
        userRole: dbUser?.role ?? null
    };
};