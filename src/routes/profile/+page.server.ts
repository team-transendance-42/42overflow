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

	
    const firstname = data.get('firstname') as string;
    const lastname = data.get('lastname') as string;
	const interests = data.get('interests') as string;
    const removeAvatar = data.get('removeAvatar') === 'true';
    const avatarFile = data.get('avatarimage') as File;

    let imageUrl: string | undefined;
    if (removeAvatar) {
      imageUrl = '';
    } else if (avatarFile && avatarFile.size > 0) {
      const uploadsDir = join('static', 'uploads');
      mkdirSync(uploadsDir, { recursive: true });

      const ext = avatarFile.name.split('.').pop();
      const filename = `${locals.user.id}.${ext}`;
      const buffer = Buffer.from(await avatarFile.arrayBuffer());
      writeFileSync(join(uploadsDir, filename), buffer);
      imageUrl = `/uploads/${filename}`;
    }

    try {
      await auth.api.updateUser({
        headers: request.headers,
        body: {
          name: `${firstname} ${lastname}`.trim(),
          ...(imageUrl !== undefined && { image: imageUrl }),
        },
      });
    } catch (e) {
      console.error('Update error:', e);
      return fail(400, { error: 'Could not update profile' });
    }


try {
  const intraprofile = data.get('intraprofile');
  const interestsRaw = data.get('interests');

  const interests = typeof interestsRaw === 'string' ? interestsRaw : null;
  const login = typeof intraprofile === 'string' && intraprofile !== '' ? intraprofile : null;

  const profile = await db.profile.upsert({
    where: { userId: locals.user.id },
    update: {
      login,
      interests,
    },
    create: {
      userId: locals.user.id,
      login,
      interests,
    },
  });

  console.log('PROFILE SAVED:', profile);
} catch (err) {
  console.error('UPDATING PROFILE FAILED:', err);
  return fail(400, { error: 'Could not update profile' });
}
  }
};