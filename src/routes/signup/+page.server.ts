import { fail, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
  signup: async ({ request }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    const password = data.get('password') as string;
    const name = data.get('name') as string;


    if (!email || !password || !name) {
      return fail(400, { error: 'All fields are required' });
    }

    try {
      await auth.api.signUpEmail({
        body: { email, password, name },
      });
    } catch (e) {
	  console.error('Signup error:', e);  
      return fail(400, { error: 'Could not create account. Email may already be in use.' });
    }

    throw redirect(303, '/login');
  }
};