import { fail, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import type { Actions, PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => 
{
  if (!locals.user) throw redirect(303, '/login');

  return {
    user: locals.user,
  };
};

export const actions: Actions = {
  update: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Not logged in' });

    const data = await request.formData();
    const avatarFile = data.get('avatarimage') as File;
	const removeAvatar = data.get('removeAvatar') === 'true';
    let imageUrl: string | null = null;

    if (avatarFile && avatarFile.size > 0) 
	{
	const allowedTypes = ['image/png', 'image/jpeg', 'image/webp'];
	if (!allowedTypes.includes(avatarFile.type)) {
    	throw error(400, 'Invalid image type');
  	}
      const uploadsDir = join('static', 'uploads');
      mkdirSync(uploadsDir, { recursive: true });
      const ext = avatarFile.type.split('/')[1];
      const filename = `${locals.user.id}.${ext}`;
      const buffer = Buffer.from(await avatarFile.arrayBuffer());
      writeFileSync(join(uploadsDir, filename), buffer);
      imageUrl = `/uploads/${filename}`;
    }

	const interests = data.get('interests') as string;
	const username = data.get('username') as string;
	const firstname = data.get('firstname') as string;
	const lastname = data.get('lastname') as string;

	const updateData: {
		interests?: string;
		name?: string;
		first_name?: string;
		last_name?: string;
		image?: string | null;
	} = {};

	if (interests) updateData.interests = interests;
	if (username) updateData.name = username;
	if (firstname) updateData.first_name = firstname;
	if (lastname) updateData.last_name = lastname;
	if (imageUrl) updateData.image = imageUrl;
	else if (removeAvatar) updateData.image = null;

	if (Object.keys(updateData).length > 0) {
		await db.user.update({
			where: { id: locals.user.id },
			data: updateData
		});
	}

	return { success: true, imageUrl };
	}
};

