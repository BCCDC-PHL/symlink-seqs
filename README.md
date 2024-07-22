[![Tests](https://github.com/BCCDC-PHL/symlink-seqs/actions/workflows/tests.yml/badge.svg)](https://github.com/BCCDC-PHL/symlink-seqs/actions/workflows/tests.yml)

# symlink-seqs

Create fastq symlinks for selected samples in sequencer output directories based on project ID from SampleSheet files.

## Usage

```
usage: symlink-seqs [-h] [-p PROJECT_ID] [-r RUN_ID] [-i IDS_FILE] [-s] [-c CONFIG] [--copy] [--csv] [--skip-qc-status-check] [--exclude-run EXCLUDE_RUN] [--excluded-runs-file EXCLUDED_RUNS_FILE]
                    [--excluded-libraries-file EXCLUDED_LIBRARIES_FILE] [-o OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT_ID, --project-id PROJECT_ID
  -r RUN_ID, --run-id RUN_ID
  -i IDS_FILE, --ids-file IDS_FILE
                        File of sample IDs (one sample ID per line)
  -s, --simplify-sample-id
                        Simplify filenames of symlinks to include only sample-id_R{1,2}.fastq.gz
  -c CONFIG, --config CONFIG
                        Config file (json format).
  --copy                Create copies instead of symlinks.
  --csv                 Print csv-format summary of fastq file paths for each sample to stdout.
  --skip-qc-status-check
                        Skip checking qc status for runs.
  --exclude-run EXCLUDE_RUN
                        A single run ID to exclude.
  --excluded-runs-file EXCLUDED_RUNS_FILE
                        File containing list of run IDs to exclude. (single column, one run ID per line, no header)
  --excluded-libraries-file EXCLUDED_LIBRARIES_FILE
                        File containing list of run ID, library ID pairs to exclude. (csv format, no header)
  -o OUTDIR, --outdir OUTDIR
                        Output directory, where symlinks (or copies) will be created.
```

If you add the `-s` (or `--simplify-sample-id`) flag, then the filenames of the symlinks will be simplified to only `sample-id_R1.fastq.gz`, instead of 
the original `sample-id_S01_L001_R1_001.fastq.gz` as they are named in the original sequencer output directory.

Adding the `--copy` flag will create copies of the files instead of symlinks. Be aware of the extra data storage implications of creating copies.

When the `--csv` flag is used, neither symlinks nor copies will be created. Instead, a csv file with the following fields will be printed to standard output:

```
ID,R1,R2
```

...where `ID` is the sample ID, `R1` is the path to the R1 fastq file, and `R2` is the path to the R2 fastq file.

If a run ID is supplied, then only samples from that run will be symlinked. If no sample IDs file is supplied, then all samples on that run will be symlinked.

### Excluded Runs and Libraries

Specific sequencing runs and libraries may be excluded when searching for fastq files to symlink.

The `--excluded-runs-file` flag can be used to provide a list of sequencing run IDs for runs to be skipped when searching for fastq files.
The file should be a simple list of sequencing run IDs with no header:

```
220318_M00123_0128_000000000-AGTBE
220521_M00456_0132_000000000-AB5RA
```

The `--excluded-libraries-file` flag can be used to provide a list of specific libraries to be skipped. The file should be a two-column, comma-separated file with no header,
with a sequencing run ID in the first column and a library ID in the second column:

```
220318_M00123_0128_000000000-AGTBE,sample-01
220318_M00123_0128_000000000-AGTBE,sample-08
220318_M00123_0128_000000000-AGTBE,sample-12
220521_M00456_0132_000000000-AB5RA,sample-06
```

## Configuration

The tool reads a config file from `~/.config/symlink-seqs/config.json` by default. An alternative config file can be provided using the `-c` or `--config` flags.

A minimal config file must include a list of directories where sequencing run dirs can be found, under the key `sequencing_run_parent_dirs`:

```json
{
	"sequencing_run_parent_dirs": [
		"/path/to/sequencer-01/output",
		"/path/to/sequencer-02/output",
		"/path/to/sequencer-03/output"
	]
}
```

Additional settings may be added to the config:

```json
{
	"sequencing_run_parent_dirs": [
		"/path/to/sequencer-01/output",
		"/path/to/sequencer-02/output",
		"/path/to/sequencer-03/output"
	],
	"simplify_sample_id": true,
	"skip_qc_status_check": true,
	"excluded_runs_file": "/path/to/excluded_runs.csv",
	"excluded_libraries_file": "/path/to/excluded_libraries.csv"
}
```

| Key                          | Required? | Value Type    | Description |
|------------------------------|-----------|---------------|-------------|
| `sequencing_run_parent_dirs` | True      | List of paths |             |
| `simplify_sample_id`         | False     | Boolean       |             |
| `copy`                       | False     | Boolean       | When set to `true`, make copies instead of symlinks               |
| `csv`                        | False     | Boolean       | When set to `true`, print a csv summary of fastq files per sample |
| `skip_qc_status_check`       | False     | Boolean       | When set to `true`, the QC status of runs will not be checked     |
| `outdir`                     | False     | Path          | Directory to create symlinks or copies under                      |
| `excluded_runs_file`         | False     | Path          | Path to file containing a list of sequencing run IDs to be excluded when searching for fastq files (single column, no header) |
| `excluded_libraries_file`    | True      | Path          | Path to file containing list of (sequencing run ID, library ID) pairs to be excluded when searching for fastq files (two columns, comma-separated) |

The file must be in valid JSON format.
