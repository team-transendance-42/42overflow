import { db } from '$lib/server/db';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals }) => {
  if (locals.user) {
    await db.user.updateMany({
      where: { id: locals.user.id },
      data: { last_seen: new Date() },
    });
  }
  return json({ ok: true });
};