import { json, error, type RequestEvent } from '@sveltejs/kit';
import { uploadProductImage } from '$lib/fileUpload.ts';
import { CommentSchema } from '$lib/zodTypes.js';
import { db } from '$lib/server/db';
import { z } from 'zod';

export const POST = async ({ locals, request, params }: RequestEvent) => {
    try {
        if (!locals.user) {
			throw error(401, 'Unauthorized');
		}

		if (!params.id) {
			throw error(400, 'Post ID is required');
		}
		const postId = parseInt(params.id);

		if (isNaN(postId)) {
			throw error(400, 'Invalid Post ID');
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

		// Create comment
		const comment = await db.comment.create({
			data: {
				content: data.content.trim(),
				parentId: data.parentId,
				postId: data.postId,
				userId: locals.user.id,
				image: imageUrl,
			}
		});

        return json({ comment }, { status: 201 });
    } catch (error) {
        console.error('Error creating comment:', error);
        if (error instanceof z.ZodError) {
            return json({
                error: 'Invalid input data',
                details: error.issues.map(e => ({
                    field: e.path.join('.'),
                    message: e.message
                }))
            }, { status: 400 });
        }
        return json({ error: 'Failed to create comment' }, { status: 500 });
    }
};
