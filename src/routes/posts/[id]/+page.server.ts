import type { PageServerLoad } from './$types.js';
import { db } from '$lib/server/db.js';

// Recursively fetch all children of a comment
async function fetchCommentWithChildren(commentId: number) {
	const comment = await db.comment.findUnique({
		where: { id: commentId },
		include: { user: true, likes: true }
	});

	if (!comment) return null;

	// Fetch and recursively process all children
	const childComments = await db.comment.findMany({
		where: { parentId: commentId },
		include: { user: true, likes: true },
		orderBy: { created_at: 'asc' }
	});

	const childrenWithNestedReplies = await Promise.all(
		childComments.map(child => fetchCommentWithChildren(child.id))
	);

	return {
		...comment,
		children: childrenWithNestedReplies.filter(Boolean)
	};
}

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
					include: { user: true }
				},
				user: true
			}
		});

        if (!postwithcomments) {
            throw (new Error('Post not found'));
        }

		// Filter root comments (parentId = null) and recursively fetch their children
		const rootComments = postwithcomments.comments.filter(c => c.parentId === null);
		const commentsWithChildren = await Promise.all(
			rootComments.map(comment => fetchCommentWithChildren(comment.id))
		);

		// Sort root comments by created_at descending
		commentsWithChildren.sort((b, a) =>
			new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
		);

		return ({
			post: {
				...postwithcomments,
				comments: commentsWithChildren
			}
		});
    } catch (error) {
        console.error('Error fetching product data:', error);
        return ({ post: null });
    }
};
