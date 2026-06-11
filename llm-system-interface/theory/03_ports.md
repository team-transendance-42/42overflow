
  "8080:80"
    ↑     ↑
    │     └── port Caddy listens on INSIDE the container
    └──────── port your Windows machine exposes to browsers

    Caddy inside the container always binds :80 and :443 — that never changes. The left side is what you type in the browser. You use 8080 instead of
  80 for the same reason as 8443 instead of 443: Windows already owns ports 80 and 443. HOST:CONTAINER — right is internal reality, left is what the
  outside world sees.