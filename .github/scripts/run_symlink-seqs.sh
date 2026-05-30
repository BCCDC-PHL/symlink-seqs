#!/bin/bash

mkdir -p artifacts/symlink-seqs

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/simulated-runs-config.json \
    --project-id 'mysterious_experiment' \
    --csv \
    > artifacts/symlink-seqs/mysterious_experiment.csv


./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --ids-file .github/data/symlink-seqs/sample_id_lists/miseq_alignment_2_samples_with_underscores.csv \
    --csv \
    > artifacts/symlink-seqs/miseq_251202_M04446_0426_000000000-M7L2J_alignment_2_samples_with_underscores.csv

