// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { User, Session } from 'better-auth';

declare global {
  namespace App {
    interface Locals {
      user: {
		id: string;
		email: string;
		role: 'USER' | 'ADMIN' | 'MODERATOR';
	  }	| null;
      session: any;
    }
  }
}

export {};
EOF