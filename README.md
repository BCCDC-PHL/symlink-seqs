# symlink-illumina-fastq-by-project-id
Create fastq symlinks for selected samples in illumina sequencer output directories based on project ID from SampleSheet.csv

## Usage

```
usage: symlink_illumina_fastq_by_project_id.py [-h] [-r RUN_DIR] [-p PROJECT_ID] [-i IDS_FILE] [-s] [-c] [-o OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  -r RUN_DIR, --run-dir RUN_DIR
  -p PROJECT_ID, --project-id PROJECT_ID
  -i IDS_FILE, --ids-file IDS_FILE
  -s, --simplify-sample-id
  -c, --copy
  -o OUTDIR, --outdir OUTDIR
```

For example:

To collect all of the fastq files from project `project-01` on run `220502_M00123_0321_000000000-AAABC` under a directory called `symlinks`, run the following:
```
symlink_illumina_fastq_by_project_id.py -r /path/to/run/220502_M00123_0321_000000000-AAABC -p project-01 -o ./symlinks
```

If you add the `-s` (or `--simplify-sample-id`) flag, then the filenames of the symlinks will be simplified to only `sample-id_R1.fastq.gz`, instead of the original `sample-id_S01_L001_R1_001.fastq.gz` as they are named in the original sequencer output directory.

Adding the `-c` (or `--copy`) flag will create copies of the files instead of symlinks. Be aware of the extra data storage implications of creating copies.
