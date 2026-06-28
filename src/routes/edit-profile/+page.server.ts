import { json, error } from '@sveltejs/kit';
import { fail, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { uploadProductImage } from '$lib/fileUpload';
import type { Actions, PageServerLoad } from './$types';
import { EditProfileSchema, type EditProfileInput } from '$lib/zodTypes';
import { z } from 'zod';

export const load: PageServerLoad = async ({ locals }) =>
{
	if (!locals.user)
		throw redirect(303, '/login');

	const user = await db.user.findFirst({
		where: { id: locals.user.id },
		select: {
			id: true,
			name: true,
			first_name: true,
			last_name: true,
			email: true,
			interests: true,
			image: true
		}
	});

	if (!user)
		throw error(404, 'User not found');

	return { user };
};

export const actions: Actions = {
	update: async ({ request, locals }) => {
		try {
			if (!locals.user)
				return fail(401, { error: 'Unauthorized' });

			// Parse and validate form data
			const formData = await request.formData();
			const data = EditProfileSchema.parse({
				id: formData.get('id') as string,
				name: formData.get('name') as string,
				first_name: formData.get('first_name') as string,
				last_name: formData.get('last_name') as string,
				interests: formData.get('interests') as string,
			});

			// Check if edited profile belongs to the logged-in user
			const loggedInUserId = locals.user.id;
			const userId = data.id;
			if (userId !== loggedInUserId)
				return fail(403, { error: 'You can only edit your own profile' });

			// Handle image upload
			let imageUrl: string | undefined = undefined;

			const imageFile = formData.get('image') as File;
			if (imageFile && imageFile.size > 0) {
				const uploadResult = await uploadProductImage(imageFile);
				if (!uploadResult.success) {
					return fail(400, { error: uploadResult.error });
				}
				imageUrl = uploadResult.url;
				console.log(`${new Date().toISOString()} - Image uploaded successfully: ${imageUrl}`);
			}

			let profileData: EditProfileInput & { image?: string | null } = {
				id: data.id,
				name: data.name,
				first_name: data.first_name,
				last_name: data.last_name,
				interests: data.interests,
			};

			// Don't update image if no new image is provided (imageUrl is null)
			if (imageUrl === undefined) {
				if (formData.get('removeImage') === 'true') {
					profileData.image = null;
				}
			} else {
				// Update with new image URL
				profileData.image = imageUrl;
			}

			console.log('Profile data to update:', profileData);

			const { id, ...toUpdateData } = profileData;

			// Edit Profile
			await db.user.update({
				where: { id: locals.user.id },
				data: toUpdateData
			});

			return { success: true };
		} catch (error) {
			console.error('Error editing profile:', error);
			if (error instanceof z.ZodError) {
				return json({
					error: 'Invalid input data',
					details: error.issues.map(e => ({
						field: e.path.join('.'),
						message: e.message
					}))
				}, { status: 400 });
			}
			return fail(500, { error: 'Internal Server Error' });
		}
	}
};

