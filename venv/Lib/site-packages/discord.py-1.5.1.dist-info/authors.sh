#!/bin/bash

# save as i.e.: git-authors and set the executable flag
git ls-tree -r -z --name-only HEAD -- $1 | xargs -0 -n1 git blame -w \
 --line-porcelain HEAD |grep  "^author "|sort|uniq -c|sort -nr
