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

./symlink-seqs\
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 240719_VH00278_220_AAFMTYGM5 \
    --project-id 'project-2' \
    --csv \
    > artifacts/symlink-seqs/nextseq_240719_VH00278_220_AAFMTYGM5_alignment_1_project-2.csv

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260514_1837_X1_FBF94296_d5e6734f \
    --csv \
    > artifacts/symlink-seqs/gridion_20260514_1837_X1_FBF94296_d5e6734f_all.csv

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260514_1837_X1_FBF94296_d5e6734f \
    --project-id 'project-1' \
    --csv \
    > artifacts/symlink-seqs/gridion_20260514_1837_X1_FBF94296_d5e6734f_project-1.csv

# GridION underscore normalization: SAMPLE_001/SAMPLE_002 in SampleSheet -> SAMPLE-001/SAMPLE-002 in output
./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260601_1200_X1_GZB00001_b1c2d3e4 \
    --csv \
    > artifacts/symlink-seqs/gridion_20260601_1200_X1_GZB00001_b1c2d3e4_all.csv
