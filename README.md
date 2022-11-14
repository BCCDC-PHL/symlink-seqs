# symlink-seqs
Create fastq symlinks for selected samples in sequencer output directories based on project ID from SampleSheet files.

## Usage

```
usage: symlink-seqs [-h] [-p PROJECT_ID] [-i IDS_FILE] [-s] [-c CONFIG] [--copy] [-o OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT_ID, --project-id PROJECT_ID
  -i IDS_FILE, --ids-file IDS_FILE
  -s, --simplify-sample-id
  -c CONFIG, --config CONFIG
  --copy
  -o OUTDIR, --outdir OUTDIR
```

If you add the `-s` (or `--simplify-sample-id`) flag, then the filenames of the symlinks will be simplified to only `sample-id_R1.fastq.gz`, instead of the original `sample-id_S01_L001_R1_001.fastq.gz` as they are named in the original sequencer output directory.

Adding the `-c` (or `--copy`) flag will create copies of the files instead of symlinks. Be aware of the extra data storage implications of creating copies.

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
| `copy`                       | False     | Boolean       | When set to `true`, make copies instead of symlinks |
| `outdir`                     | False     | Path          | Directory to create symlinks or copies under        |

The file must be in valid JSON format.
