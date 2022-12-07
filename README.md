# symlink-seqs
Create fastq symlinks for selected samples in sequencer output directories based on project ID from SampleSheet files.

## Usage

```
usage: symlink-seqs [-h] [-p PROJECT_ID] [-r RUN_ID] [-i IDS_FILE] [-s] [-c CONFIG] [--copy] [--csv] [-o OUTDIR]

optional arguments:
  -h, --help                                Show this help message and exit.
  -p PROJECT_ID, --project-id PROJECT_ID
  -r RUN_ID, --run-id RUN_ID
  -i IDS_FILE, --ids-file IDS_FILE          File of sample IDs (one sample ID per line)
  -s, --simplify-sample-id                  Simplify filenames of symlinks to include only sample-id_R{1,2}.fastq.gz
  -c CONFIG, --config CONFIG                Config file (json format).
  --copy                                    Create copies instead of symlinks.
  --csv                                     Print csv-format summary of fastq file paths for each sample to stdout.
  -o OUTDIR, --outdir OUTDIR                Output directory, where symlinks (or copies) will be created.
```

If you add the `-s` (or `--simplify-sample-id`) flag, then the filenames of the symlinks will be simplified to only `sample-id_R1.fastq.gz`, instead of 
the original `sample-id_S01_L001_R1_001.fastq.gz` as they are named in the original sequencer output directory.

Adding the `--copy` flag will create copies of the files instead of symlinks. Be aware of the extra data storage implications of creating copies.

When the `--csv` flag is used, neither symlinks nor copies will be created. Instead, a csv file with the following fields will be printed to standard output:

```
ID,R1,R2
```

...where `ID` is the sample ID, `R1` is the path to the R1 fastq file, and `R2` is the path to the R2 fastq file.

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
	"simplify_sample_id": true
}
```

| Key                          | Required? | Value Type    | Description |
|------------------------------|-----------|---------------|-------------|
| `sequencing_run_parent_dirs` | True      | List of paths |             |
| `simplify_sample_id`         | False     | Boolean       |             |
| `copy`                       | False     | Boolean       | When set to `true`, make copies instead of symlinks               |
| `csv`                        | False     | Boolean       | When set to `true`, print a csv summary of fastq files per sample |
| `outdir`                     | False     | Path          | Directory to create symlinks or copies under                      |

The file must be in valid JSON format.
