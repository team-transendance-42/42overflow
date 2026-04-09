// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { User, Session } from 'better-auth';

declare global {
  namespace App {
    interface Locals {
      user: any;
      session: any;
    }
  }
}

export {};
EOF
