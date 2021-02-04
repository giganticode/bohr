if [ -n "$(git --no-pager diff HEAD~1 Dockerfile)" ]; then
    docker build --tag giganticode/bohr-cml-base:latest .
    docker push giganticode/bohr-cml-base:latest
else
    echo "Dockerfile hasn't change."
fi