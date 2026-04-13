import { redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.user) throw redirect(303, '/login');

  const profile = await db.profile.findUnique({
    where: { userId: locals.user.id }
  });

  return {
    user: locals.user,
    profile
  };
};