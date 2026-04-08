import { fail, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
  login: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    const password = data.get('password') as string;

    if (!email || !password) {
      return fail(400, { error: 'Email and password are required' });
    }

    try {
      const result = await auth.api.signInEmail({
        body: { email, password },
      });

      cookies.set('better-auth.session_token', result.token, {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 7,
      });
    } catch (e) {
      return fail(401, { error: 'Invalid email or password' });
    }

    throw redirect(303, '/');
  }
};