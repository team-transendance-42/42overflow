import * as z from "zod";

// id validation schema
export const IdSchema = z.object({
    id: z.number('id Has to be a number').int('id Has to be an integer').positive('id Has to be a positive number')
});

// Image file schema
const ImageFileSchema = z.object({
    name: z.string(),
    size: z.number().max(5 * 1024 * 1024, { message: "Image size must be less than 5MB." }),
    type: z.string().refine(
        (type) => ['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(type),
        "Only JPEG, PNG, WebP and GIF files are allowed"
    )
})

// Comment schema
export const CommentSchema = z.object({
	postId: z.number().int().positive(),
    parentId: z.number().int().positive().nullable().optional(),
	content: z.string().min(1).max(500),
});

export const CommentWithImageSchema = CommentSchema.extend({
	image: ImageFileSchema.optional(),
});

export type CommentInput = z.infer<typeof CommentSchema>;
export type CommentWithImageInput = z.infer<typeof CommentWithImageSchema>;

// Post schema
export const PostSchema = z.object({
	postId: z.number().int().positive(),
	title: z.string().min(1).max(100),
	content: z.string().min(1).max(500),
});

export type PostInput = z.infer<typeof PostSchema>;
