  Docker cache types (docker system df shows all):
    ┌─────────────┬────────────────────────────────────────────────┐
  │    Type     │                   What it is                   │
  ├─────────────┼────────────────────────────────────────────────┤
  │ Images      │ Downloaded/built images                        │
  ├─────────────┼────────────────────────────────────────────────┤
  │ Containers  │ Stopped container filesystems                  │
  ├─────────────┼────────────────────────────────────────────────┤
  │ Volumes     │ Named volumes (postgres-data, ollama-data etc) │
  ├─────────────┼────────────────────────────────────────────────┤
  │ Build cache │ Every intermediate layer ever built            │
  └─────────────┴────────────────────────────────────────────────┘
  
  Every --build creates new layer snapshots. Old ones aren't deleted
  automatically — Docker keeps them in case you roll back or reuse them.
  Each rebuild of a layer that changed adds a new snapshot on top of
  old ones. They accumulate indefinitely.

  Cleanup:
  docker system prune          # removes stopped containers, dangling
  images, unused build cache
  docker builder prune         # build cache only
  docker system prune -a       # everything not currently in use
  (aggressive)
  Docker never cleans up automatically unless you run one of these.