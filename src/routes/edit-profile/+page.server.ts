import { fail, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import { db } from '$lib/server/db';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) throw redirect(303, '/login');

  // also load user-specific fields
//   const profile = await db.user.findUnique({
//     where: { id: locals.user.id }
//   });

  return {
    user: locals.user,
    // profile
  };
};

export const actions: Actions = {
  update: async ({ request, locals }) => {
    if (!locals.user) return fail(401, { error: 'Not logged in' });

    const data = await request.formData();
    const avatarFile = data.get('avatarimage') as File;

    let imageUrl: string | null = null;

    if (avatarFile && avatarFile.size > 0) {
      const uploadsDir = join('static', 'uploads');
      mkdirSync(uploadsDir, { recursive: true });
      const ext = avatarFile.name.split('.').pop();
      const filename = `${locals.user.id}.${ext}`;
      const buffer = Buffer.from(await avatarFile.arrayBuffer());
      writeFileSync(join(uploadsDir, filename), buffer);
      imageUrl = `/uploads/${filename}`;
    }

    await db.user.update({
      where: { id: locals.user.id },
      data: {
        login: data.get('intraprofile') as string || undefined,
        interests: data.get('interests') as string || undefined,
        name: data.get('username') as string || undefined,
      },
    });

	const firstname = data.get('firstname');
	const lastname = data.get('lastname');

	const updateData: {
		first_name?: string;
		last_name?: string;
		image?: string;
	} = {};

	// Create an update object only with the fields that are provided
	if (typeof firstname === 'string' && firstname !== undefined) {
		updateData.first_name = firstname;
	}
	if (typeof lastname === 'string' && lastname !== undefined) {
		updateData.last_name = lastname;
	}
	if (imageUrl) {
		updateData.image = imageUrl;
	}

	// Only perform the update if there are fields to update
	if (Object.keys(updateData).length > 0) {
		await db.user.update({
			where: { id: locals.user.id },
			data: updateData
		});
	}

	return { success: true, imageUrl };
	}
};

