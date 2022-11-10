#!/usr/bin/env python

import argparse
import glob
import json
import logging
import os
import shutil
import re

def jdump(x):
    print(json.dumps(x, indent=2))


def parse_config(config_path):
    """
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


# https://stackoverflow.com/a/1176023
def camel_to_snake(name):
    """
    Convert camelCase strings to snake_case strings
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def determine_sequencer_type(run_id):
    """
    Determine sequencer type based on format of Run ID
    Returns str ("miseq" or "nextseq")
    """
    miseq_regex = '\d{6}_M\d{5}_\d{4}_\d{9}-[A-Z0-9]{5}'
    nextseq_regex = '\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}'
    sequencer_type = None
    if re.match(miseq_regex, run_id):
        sequencer_type = "miseq"
    elif re.match(nextseq_regex, run_id):
        sequencer_type = "nextseq"

    return sequencer_type


def parse_samplesheet_miseq(samplesheet_path):
    """
    Parse a MiSeq SampleSheet to get sample and project IDs
    """
    data = []
    with open(samplesheet_path, 'r') as f:
        for line in f:
            if not line.strip().startswith('[Data]'):
                continue
            else:
                break
          
        data_header = [x.lower() for x in next(f).strip().split(',')]
      
        for line in f:
            if not all([x == '' for x in line.strip().split(',')]):
                data_line = {}
                for idx, data_element in enumerate(line.strip().split(',')):
                    try:
                        data_line[data_header[idx]] = data_element
                    except IndexError as e:
                        pass
                data.append(data_line)

    return data


def parse_samplesheet_nextseq(samplesheet_path):
    """
    Parse a NextSeq SampleSheet to get sample and project IDs
    """
    cloud_data_lines = []
    cloud_data = []
    with open(samplesheet_path, 'r') as f:
        for line in f:
            if line.strip().startswith('[Cloud_Data]'):
                break
        for line in f:
            if line.strip().startswith('[Cloud_Settings]') or line.strip().rstrip(',') == "":
                break
            cloud_data_lines.append(line.strip().rstrip(','))

    if cloud_data_lines:
        cloud_data_keys = [camel_to_snake(x) for x in cloud_data_lines[0].split(',')]
        for line in cloud_data_lines[1:]:
            d = {}
            values = line.strip().split(',')
            if not all([x == '' for x in values]):
                for idx, key in enumerate(cloud_data_keys):
                    try:
                        d[key] = values[idx]
                    except IndexError as e:
                        d[key] = ""
                cloud_data.append(d)
  
    return cloud_data


def has_necessary_fields_for_symlinking_miseq(sample):
    """
    Check if a 'sample' dictionary has the necessary fields for symlinking
    Returns bool (True if ready for symlinking, false otherwise)
    """
    selected = False
    conditions = []
    if 'sample_name' in sample and sample['sample_name'] != "":
        conditions.append(True)
    elif 'sample_id' in sample and sample['sample_id'] != "":
        sample['sample_name'] = sample['sample_id']
        conditions.append(True)
    else:
        conditions.append(False)

    if 'sample_project' in sample and sample['sample_project'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if all(conditions):
        selected = True

    return selected


def has_necessary_fields_for_symlinking_nextseq(sample):
    """
    Check if a 'sample' dictionary has the necessary fields for symlinking
    Returns bool (True if ready for symlinking, false otherwise)
    """
    selected = False
    conditions = []
    if 'sample_id' in sample and sample['sample_id'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if 'project_name' in sample and sample['project_name'] != "":
        conditions.append(True)
    else:
        conditions.append(False)

    if all(conditions):
        selected = True

    return selected


def get_latest_analysis_subdir(run_dir):
    analysis_subdirs = os.listdir(os.path.join(run_dir, "Analysis"))
    latest_analysis_subdir_num = analysis_subdirs[-1]
    latest_analysis_subdir = os.path.abspath(os.path.join(run_dir, "Analysis", latest_analysis_subdir_num))
    
    return latest_analysis_subdir


def get_src_dest_paths(samples, sequencer_type, run_dir, outdir, simplify_sample_id):
    """
    samples: List of dicts, with keys "sample_name" OR "sample_id"
    sequencer_type: str ("miseq" or "nextseq")
    run_dir: path to illumina sequencer output directory
    outdir: destination dir to create symlinks or copies
    simplify_sample_id: bool If True, sample ID will be truncated at first '_' char.

    Returns a list of dicts with keys "src", "dest" and "sample_id"
    """
    src_dest = []
    fastq_subdir = None
    if sequencer_type == "miseq":
        fastq_subdir = "Data/Intensities/BaseCalls"
    elif sequencer_type == "nextseq":
        fastq_subdir = os.path.join(get_latest_analysis_subdir(run_dir), 'Data', 'fastq')
    for sample in samples:
        sample_id = None
        if sequencer_type == 'miseq':
            sample_id = sample['sample_name']
        elif sequencer_type == 'nextseq':
            sample_id = sample['sample_id']
        sample_fastq_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample_id + '_*.fastq'))
        sample_fastq_gz_files = glob.glob(os.path.join(run_dir, fastq_subdir, sample_id + '_*.fastq.gz'))
        for sample_fastq_file in sample_fastq_files + sample_fastq_gz_files:
            if os.path.exists(sample_fastq_file):
                src = os.path.abspath(sample_fastq_file)
                dest_filename = os.path.basename(sample_fastq_file)
                sample_id = dest_filename.split('_')[0]
                if simplify_sample_id:
                    read = ""
                    if re.search('_R1_', dest_filename):
                        read = 'R1'
                    elif re.search('_R2_', dest_filename):
                        read = 'R2'
                    extension = '.fastq'
                    if dest_filename.split('.')[-1] == 'gz':
                        extension += '.gz'
                    dest_filename = sample_id + '_' + read + extension

                dest = os.path.join(outdir, dest_filename)

                src_dest.append({"src": src, "dest": dest, "sample_id": sample_id})

    return src_dest        


def create_symlinks(src_dest_paths):
    """
    src_dest_paths: list of dicts with keys "src" and "dest"
    Symlink src to dest for each element in src_dest_paths
    """
    for paths in src_dest_paths:
        outdir = os.path.dirname(paths['dest'])
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        try:
            os.symlink(paths['src'], paths['dest'])
        except OSError as e:
            print(str(e) + ". files: " + paths['src'] + ", " + paths['dest'])


def create_copies(src_dest_paths):
    """
    src_dest_paths: list of dicts with keys "src" and "dest"
    Copy src to dest for each element in src_dest_paths
    """
    for paths in src_dest_paths:
        outdir = os.path.dirname(paths['dest'])
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        shutil.copy(paths['src'], paths['dest'])


def parse_ids_file(ids_file_path):
    """
    """
    sample_ids = set()
    with open(ids_file_path, 'r') as f:
        for line in f:
            sample_ids.add(line.strip())

    return sample_ids


def main(args):
    
    config = parse_config(args.config)

    sequencing_run_parent_dirs = config['sequencing_run_parent_dirs']
    
    sample_ids = parse_ids_file(args.ids_file)

    for run_parent_dir in sequencing_run_parent_dirs:
        run_parent_dir_contents = list(map(lambda x: os.path.abspath(os.path.join(run_parent_dir, x)), os.listdir(run_parent_dir)))
        
        run_dirs = list(filter(lambda x: os.path.isdir(x), run_parent_dir_contents))

        for run_dir in run_dirs:
            run_id = os.path.basename(run_dir.rstrip('/'))
            sequencer_type = determine_sequencer_type(run_id)

            if sequencer_type == 'miseq':
                samplesheet_path = os.path.join(run_dir, 'SampleSheet.csv')
                all_samples = parse_samplesheet_miseq(samplesheet_path)
                candidate_samples = filter(has_necessary_fields_for_symlinking_miseq, all_samples)
                selected_samples = filter(lambda x: x['sample_id'] in sample_ids or x['sample_name'] in sample_ids, candidate_samples)
        
            elif sequencer_type == 'nextseq':
                analysis_subdir = get_latest_analysis_subdir(run_dir)
                samplesheet_paths = glob.glob(os.path.join(analysis_subdir, 'Data', 'SampleSheet*.csv'))
                samplesheet_path = samplesheet_paths[0] # If multiple samplesheets exist, how do we choose the correct one?
                all_samples = parse_samplesheet_nextseq(samplesheet_path)
                candidate_samples = filter(has_necessary_fields_for_symlinking_nextseq, all_samples)
                selected_samples = filter(lambda x: x['sample_id'] in sample_ids, candidate_samples)

            src_dest_paths = get_src_dest_paths(selected_samples, sequencer_type, run_dir, args.outdir, args.simplify_sample_id)

            if args.copy:
                create_copies(src_dest_paths)
            else:
                create_symlinks(src_dest_paths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project-id')
    parser.add_argument('-i', '--ids-file', required=True)
    parser.add_argument('-s', '--simplify-sample-id', action='store_true')
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('--copy', action='store_true')
    parser.add_argument('-o', '--outdir', default='.')
    args = parser.parse_args()
    main(args)
