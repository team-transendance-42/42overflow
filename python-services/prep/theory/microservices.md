Best practice for microservices:

Each service (rag, speach-to-text, etc.) runs in its own container.
This is the standard in Docker/microservice architecture: isolation, independent scaling, and easier debugging.
Yes, this means each container has its own Python install and dependencies, but this is normal and expected.
Why not combine?

Combining multiple services into one container (a “fat” container) makes deployment, scaling, and updates harder.
If one service crashes or needs an update, you have to restart/rebuild the whole container.
Security and dependency management become more complex.
How to optimize resource usage:

Use slim base images (as you do).
Share Docker build cache layers (Docker does this automatically).
If you deploy to production, use orchestration (like Docker Compose or Kubernetes) to manage resources and scaling.