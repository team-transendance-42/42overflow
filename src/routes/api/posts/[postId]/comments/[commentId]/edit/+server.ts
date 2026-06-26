import { json, error, type RequestEvent } from '@sveltejs/kit';
import { uploadProductImage } from '$lib/fileUpload';
import { CommentSchema } from '$lib/zodTypes.js';
import { db } from '$lib/server/db';
import { z } from 'zod';
import { broadcast } from '$lib/server/sse';

export const POST = async ({ locals, request, params }: RequestEvent) => {
    try {
        if (!locals.user) {
			throw error(401, 'Unauthorized');
		}

		if (!params.postId) {
			throw error(400, 'Post ID is required');
		}
		const postId = parseInt(params.postId);
		if (isNaN(postId)) {
			throw error(400, 'Invalid Post ID');
		}

        if (!params.commentId) {
			throw error(400, 'Comment ID is required');
		}
		const commentId = parseInt(params.commentId);
		if (isNaN(commentId)) {
			throw error(400, 'Invalid Comment ID');
		}

        // Get the comment to verify ownership
		const comment = await db.comment.findUnique({
			where: { id: commentId }
		});

		if (!comment) {
			throw error(404, 'Comment not found');
		}

		// Check if the user owns the comment
		if (comment.userId !== locals.user.id) {
			throw error(403, 'You can only edit your own comments');
		}

        const formData = await request.formData();

        // Extract form fields and convert types
        const parentIdValue = formData.get('parentId');
        const commentData = {
			postId: postId,
            parentId: parentIdValue ? parseInt(parentIdValue as string) : null,
			content: formData.get('content') as string,
		}

		const data = CommentSchema.parse(commentData);

        // Handle image upload
        let imageUrl = null;

        const imageFile = formData.get('image') as File;
        if (imageFile && imageFile.size > 0) {
            const uploadResult = await uploadProductImage(imageFile);
            if (!uploadResult.success) {
                return json({ error: uploadResult.error }, { status: 400 });
            }
            imageUrl = uploadResult.url;
            console.log(`${new Date().toISOString()} - Image uploaded successfully: ${imageUrl}`);
        }

        let toUpdateData: any = {
            content: data.content.trim(),
			isEdited: true,
        };

        // Don't update image if no new image is provided (imageUrl is null)
        if (imageUrl === null) {
            if (formData.get('removeImage') === 'true') {
                toUpdateData.image = null;
            }
        } else {
            // Update with new image URL
            toUpdateData.image = imageUrl;
        }

		// Edit comment
		const editedComment = await db.comment.update({
			where: { id: commentId },
			data: toUpdateData,
		});

        // re-fetch with relations if needed
        const fullComment = await db.comment.findUnique({
            where: { id: commentId },
            include: {
                user: true,
                likes: true
            }
        });

        broadcast({
            type: 'comment-update',
            comment: {
                ...fullComment,
                likeCount: fullComment.likes.length
            }
        });

        return json({ comment: editedComment }, { status: 201 });
    } catch (error) {
        console.error('Error editing comment:', error);
        if (error instanceof z.ZodError) {
            return json({
                error: 'Invalid input data',
                details: error.issues.map(e => ({
                    field: e.path.join('.'),
                    message: e.message
                }))
            }, { status: 400 });
        }
        return json({ error: 'Failed to edit comment' }, { status: 500 });
    }
};
