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
    await db.user.update({
      where: { id: session.user.id },
      data: { last_seen: new Date() },
    });
  }


  return resolve(event);
};