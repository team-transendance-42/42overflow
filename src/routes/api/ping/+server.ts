import { db } from '$lib/server/db';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals }) => {
  if (locals.user) {
    await db.profile.updateMany({
      where: { userId: locals.user.id },
      data: { lastSeen: new Date() },
    });
  }
  return json({ ok: true });
};