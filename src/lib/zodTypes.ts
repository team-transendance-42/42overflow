import * as z from "zod";

// id validation (e.g. 1, 2, 3)
export const IdSchema = z.object({
    id: z.number({ message: "ID has to be a number" }).int({ message: "ID has to be an integer" }).positive({ message: "ID has to be a positive number" })
});

// id string validation (e.g OdPthUHbePkNPADAyQGDe1Ez1db6ziPj)
export const idStringSchema = z.object({
    id: z.string().min(1, { message: "ID is required." })
});

// Comment
export const CommentSchema = z.object({
    postId: IdSchema.shape.id,
    parentId: IdSchema.shape.id.nullable().optional(),
	content: z.string().min(1, { message: "Content is required." }).max(500, { message: "Content must be between 1 and 500 characters." }),
});

export type CommentInput = z.infer<typeof CommentSchema>;

// Post
export const PostSchema = z.object({
	postId: IdSchema.shape.id,
	title: z.string().min(1, { message: "Title is required." }).max(100, { message: "Title must be between 1 and 100 characters." }),
	content: z.string().min(1, { message: "Content is required." }).max(500, { message: "Content must be between 1 and 500 characters." }),
});

export type PostInput = z.infer<typeof PostSchema>;

export const CreatePostSchema = z.object({
	title: z.string().min(1, { message: "Title is required." }).max(75, { message: "Title must be between 1 and 75 characters." }),
    subjectId: IdSchema.shape.id,
	content: z.string().min(1, { message: "Content is required." }).max(500, { message: "Content must be between 1 and 500 characters." }),
});

export type CreatePostInput = z.infer<typeof CreatePostSchema>;

// Subject
export const SubjectDescriptionSchema = z.object({
    description: z.string().max(500, { message: "Description must be less than 500 characters." }).optional(),
});

export const CreateSubjectSchema = z.object({
    name: z.string().min(1, { message: "Name is required." }).max(50, { message: "Name must be between 1 and 50 characters." }),
    description: SubjectDescriptionSchema.shape.description,
});

export type SubjectDescriptionInput = z.infer<typeof SubjectDescriptionSchema>;
export type CreateSubjectInput = z.infer<typeof CreateSubjectSchema>;


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
