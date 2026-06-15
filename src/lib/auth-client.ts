import { createAuthClient } from 'better-auth/svelte';

// No baseURL — defaults to window.location.origin, works on any port (dev :5173, Docker :8080, production domain).
export const authClient = createAuthClient();