import { auth } from '$lib/server/auth';
import { db } from '$lib/server/db';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const session = await auth.api.getSession({
    headers: event.request.headers,
  });

  event.locals.user = session?.user ?? null;
  event.locals.session = session?.session ?? null;

   if (session?.user) {
    await db.profile.updateMany({
      where: { userId: session.user.id },
      data: { lastSeen: new Date() },
    });
  }


  return resolve(event);
};