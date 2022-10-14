#! /bin/bash

set -e -x

exec docker run \
    --interactive \
    --tty \
    --volume $(pwd):/workdir \
    --workdir /workdir \
    fkrull/multi-python \
    "$@"
