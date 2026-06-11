. Start with symptoms — "login hangs" means a request never returns. Could be: network timeout, DB down, app crash, redirect loop.
  2. Check the app logs first — not postgres, not caddy. The app is the one processing the login request, so its logs have the most context.
  3. Scan for WARN/ERROR lines — ignore the noise (normal Prisma queries), look for anything that says "could not", "missing", "failed", "warn",
  "error".
  4. Read what the warning says literally — Base URL could not be determined. Without this, callbacks and redirects may not work correctly. —
  that's exactly "login hangs on redirect."
  5. Cross-reference with .env — the warning told us BETTER_AUTH_URL env var is needed.
  ====================

   General rule: when something "hangs" (not crashes), it's almost always:
  - a redirect that goes to the wrong place, OR
  - a request waiting on something that never responds (DB timeout, missing service)

  The logs tell you which one.
