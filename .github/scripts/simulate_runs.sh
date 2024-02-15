#!/bin/bash

timeout 10 java -jar illumina-run-simulator.jar \
	--config .github/data/illumina-run-simulator/config.edn \
	2> >(tee artifacts/illumina-run-simulator.log.jsonl) \
    || code=$?;

if [[ $code -ne 124 && $code -ne 0 ]]; then
    exit $code;
fi

.github/scripts/add_qc_check_complete.py --simulated-runs-dir artifacts/simulated_runs

.github/scripts/copy_samplesheets.py --simulated-runs-dir artifacts/simulated_runs
