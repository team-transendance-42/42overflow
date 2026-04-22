import { fail, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import { db } from '$lib/server/db';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) throw redirect(303, '/login');
  
  // also load profile-specific fields
  const profile = await db.profile.findUnique({
    where: { userId: locals.user.id }
  });

  return { 
    user: locals.user,
    profile 
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

    await db.profile.upsert({
      where: { userId: locals.user.id },
      update: {
        login: data.get('intraprofile') as string || undefined,
        interests: data.get('interests') as string || undefined,
        username: data.get('username') as string || undefined,
      },
      create: {
        userId: locals.user.id,
        login: data.get('intraprofile') as string || undefined,
        interests: data.get('interests') as string || undefined,
        username: data.get('username') as string || undefined,
      },
    });

	const firstname = data.get('firstname') as string;
	const lastname = data.get('lastname') as string;
	const fullName = [firstname, lastname].filter(Boolean).join(' ').trim();

	if (fullName) {
  		await db.user.update({
    		where: { id: locals.user.id },
    		data: { name: fullName }
  	});
	}

    if (imageUrl) {
  		await db.user.update({
    		where: { id: locals.user.id },
    		data: { image: imageUrl }
  		});
	}

	return { success: true, imageUrl };
 	 }
	};

