import { fail } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import { db } from '$lib/server/db';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request }) => {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session) return { user: null };
  return { user: session.user };
};

export const actions: Actions = {
  update: async ({ request }) => {
    const session = await auth.api.getSession({ headers: request.headers });
    if (!session) return fail(401, { error: 'Not logged in' });

    const data = await request.formData();
    const firstname = data.get('firstname') as string;
    const lastname = data.get('lastname') as string;
    const email = data.get('email') as string;
    const avatarFile = data.get('avatarimage') as File;

    let imageUrl: string | undefined;

    // handle file upload if a file was provided
    if (avatarFile && avatarFile.size > 0) {
      const uploadsDir = join('static', 'uploads');
      mkdirSync(uploadsDir, { recursive: true });

      const ext = avatarFile.name.split('.').pop();
      const filename = `${session.user.id}.${ext}`;
      const buffer = Buffer.from(await avatarFile.arrayBuffer());
      writeFileSync(join(uploadsDir, filename), buffer);
      imageUrl = `/uploads/${filename}`;
    }

    // update name + email via better-auth
    try {
      await auth.api.updateUser({
        headers: request.headers,
        body: {
          name: `${firstname} ${lastname}`.trim(),
          ...(imageUrl && { image: imageUrl }),
        },
      });
    } catch (e) {
      console.error('Update error:', e);
      return fail(400, { error: 'Could not update profile' });
    }

    // update profile-specific fields in your Profile table
    await db.profile.upsert({
      where: { userId: session.user.id },
      update: {
        login: data.get('intraprofile') as string || undefined,
        campusId: null, // wire up later
      },
      create: {
        userId: session.user.id,
        login: data.get('intraprofile') as string || undefined,
      },
    });

    return { success: true };
  }
};