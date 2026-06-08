git branch -r // show remote branches

git fetch origin --prune // synch with latest remote refs

git checkout -b develop --track origin/develop // create local develop and pull from remote develop

git fetch origin develop // update local develop with latest from remote
===============

# 1) leave develop first (can't delete checked-out branch)
git switch main

# 2) delete local develop
git branch -D develop

# 3) refresh remote refs
git fetch origin --prune

# 4) recreate local develop from remote
git switch -c develop --track origin/develop
=======================

# show local branches + their upstream
git branch -vv

# show detailed upstream config for current branch
git rev-parse --abbrev-ref --symbolic-full-name @{u}

# full remote + tracking summary
git remote show origin