import * as z from "zod";

// id validation
export const IdSchema = z.object({
    id: z.number('id Has to be a number').int('id Has to be an integer').positive('id Has to be a positive number')
});

// id string validation (e.g OdPthUHbePkNPADAyQGDe1Ez1db6ziPj)
export const idStringSchema = z.object({
    id: z.string().min(1, 'id Has to be a non-empty string')
});

// Comment
export const CommentSchema = z.object({
    postId: IdSchema.shape.id,
    parentId: IdSchema.shape.id.nullable().optional(),
	content: z.string().min(1).max(500),
});

export type CommentInput = z.infer<typeof CommentSchema>;

// Post
export const PostSchema = z.object({
	postId: IdSchema.shape.id,
	title: z.string().min(1).max(100, { message: "Title must be between 1 and 100 characters." }),
	content: z.string().min(1).max(500, { message: "Content must be between 1 and 500 characters." }),
});

export type PostInput = z.infer<typeof PostSchema>;

// Profile
const NameSchema = z.object({
    name: z.string().min(1, { message: "Name is required." }).max(25, { message: "Name must be less than 25 characters." }),
});

const optionalName = z.preprocess(
    value => value === '' ? undefined : value,
    NameSchema.shape.name.optional()
);

export const EditProfileSchema = z.object({
    id: idStringSchema.shape.id,
    name: optionalName,
    first_name: optionalName,
    last_name: optionalName,
    interests: z.string().optional(),
})

export type EditProfileInput = z.infer<typeof EditProfileSchema>;
