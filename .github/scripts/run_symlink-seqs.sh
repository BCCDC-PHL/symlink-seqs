#!/bin/bash

mkdir -p artifacts/symlink-seqs

./symlink-seqs \
    --config .github/data/symlink-seqs/config.json \
    --project-id 'mysterious_experiment' \
    --csv \
    -o artifacts/symlinks/mysterious_experiment \
    > artifacts/symlink-seqs/mysterious_experiment.csv
