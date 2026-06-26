docker system prune -a --volumes -f // cleaned remaining resources

docker system df // 

Remove unused images:
docker image prune -a

Remove unused build cache:
docker builder prune -a

Full cleanup of unused Docker objects:
docker system prune -a