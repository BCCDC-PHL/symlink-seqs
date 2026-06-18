#!/bin/bash

rm -rf artifacts/symlink-seqs

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

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 240719_VH00278_220_AAFMTYGM5 \
    --project-id 'project-2' \
    --csv \
    > artifacts/symlink-seqs/nextseq_240719_VH00278_220_AAFMTYGM5_alignment_1_project-2.csv

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260601_SH00789_0007_ASCQ2G973-SC3 \
    --ids-file .github/data/symlink-seqs/sample_id_lists/i100_selected_samples.csv \
    --csv \
    > artifacts/symlink-seqs/i100_20260601_SH00789_0007_ASCQ2G973-SC3_selected_samples.csv

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

# GridION underscore project IDs: alias format SAMPLE-001_ecoli_test -> project ID ecoli_test preserved
./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260601_1200_X1_GZB00001_b1c2d3e4 \
    --csv \
    > artifacts/symlink-seqs/gridion_20260601_1200_X1_GZB00001_b1c2d3e4_all.csv

./symlink-seqs \
    --config .github/data/symlink-seqs/configs/test_run_dirs_config.json \
    --run-id 20260601_1200_X1_GZB00001_b1c2d3e4 \
    --project-id 'ecoli_test' \
    --csv \
    > artifacts/symlink-seqs/gridion_20260601_1200_X1_GZB00001_b1c2d3e4_ecoli_test.csv
