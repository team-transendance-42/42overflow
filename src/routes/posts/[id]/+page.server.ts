import type { PageServerLoad } from './$types.js';
import { db } from '$lib/server/db.js';


export const load: PageServerLoad = async ({ params }) => {
    try {
        if (!params.id) {
            return ({ post: null });
        }
		const postIdNum = parseInt(params.id);
		if (isNaN(postIdNum)) {
			return ({ post: null });
		}

		const postwithcomments = await db.post.findUnique({
			where: { id: postIdNum },
			include: {
				comments: {
					orderBy: { created_at: 'desc' },
					include: { user: true }
				},
				user: true
			}
		});

        if (!postwithcomments) {
            throw (new Error('Post not found'));
        }

        return ({ post: postwithcomments });
    } catch (error) {
        console.error('Error fetching product data:', error);
        return ({ post: null });
    }
};
