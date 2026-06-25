Thread pool — only 1 thread/

  Not quite. Python's async event loop runs on one thread, but asyncio.to_thread() spawns a worker 
  thread from a background pool. Here's why that matters:

  Event loop thread           Worker thread (from pool)
  ─────────────────           ─────────────────────────
  handles HTTP requests  →    runs fastembed CPU math
  keeps answering users  ←    returns result when done

  Without asyncio.to_thread, FastEmbed would freeze the event loop for 100–300ms — no other request
  could be answered during that time. With it, the loop stays free while the CPU crunches numbers on a
  separate thread.

  "Thread pool" = Python's default ThreadPoolExecutor, which keeps a few worker threads alive. You
  don't manage it — asyncio.to_thread() borrows one automatically.

