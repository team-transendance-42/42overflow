import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
  logout: async ({ request, cookies }) => {
    await auth.api.signOut({
      headers: request.headers,
    });

    cookies.delete('better-auth.session_token', { path: '/' });

    throw redirect(303, '/login');
  }
};