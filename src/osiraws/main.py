import argparse
import os
import numpy as np
from tqdm import tqdm
import h5py
from shutil import copy2
from pathlib import Path
import sys
 

def copy_tree(src, dst):
    src = Path(src)
    dst = Path(dst)

    # [sys.stdout.write(p) for p in src.rglob('*.h5') if p.is_file()]
    files = [p for p in src.rglob('*.h5') if p.is_file()]

    for f in tqdm(files, desc='[1/2] Copying files'):
        rel = f.relative_to(src)
        target = dst / rel
        
        copy2(f, target)

def output_dir(out_path):
    if out_path is None:
        out_path = os.path.join(args.sim_dir, f'MS/RAW/{args.species}_SORTED')
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
        
    if not os.path.isabs(out_path):
        out_path = os.path.join(args.sim_dir, args.output)
    
    return out_path

def open_from_index(i, data_dir, file_prefix):
    fname = os.path.join(data_dir, file_prefix + f'-{i:06}.h5')
    return fname

def list_routine(args):
    raw_dir = os.path.join(args.sim_dir, 'MS/RAW/')
    for path in Path(raw_dir).iterdir():
        sys.stdout.write(path.name+'\n')

def sort_routine(args):
    orig = os.path.join(args.sim_dir, f'MS/RAW/{args.species}')
    out = output_dir(args.output)
    sys.stdout.write('Selected species: ' + args.species+'\n')
    sys.stdout.write('Original directory: ' + orig+'\n')
    sys.stdout.write('Target directory: ' + out+'\n')
    if not args.skip_copy:
        copy_tree(orig, out)

    out = Path(out)
    files = [p for p in out.rglob('*.h5') if p.is_file()]
    file_prefix = f'RAW-{args.species}'
    frame_indices = [int(str(f).split('-')[-1].split('.')[0]) for f in sorted(files)]
    if args.start_at is not None:
        sys.stdout.write(f'--start_at flag was invoked, starting at frame index {args.start_at}/{len(frame_indices)}' +'\n')
        frame_indices = frame_indices[args.start_at:]

    for i in tqdm(range(len(frame_indices)), desc='[2/2] Sorting raw data'):
        with h5py.File(open_from_index(frame_indices[i], out, file_prefix), 'r+') as f:
            ind_sorted = np.lexsort((f['tag'][:,1], f['tag'][:,0]))
            for key in f.keys():
                if key == 'tag':
                    sorted_temp = f[key][:][ind_sorted, :]
                elif key == 'SIMULATION':
                    continue
                else:
                    sorted_temp = f[key][:][ind_sorted]
                    
                f[key][:] = sorted_temp 

def validate(args):
    out = output_dir(args.raw_dir)
    out = Path(out)
    files = sorted([p for p in out.rglob('*.h5') if p.is_file()])
    frame_indices = [int(str(f).split('-')[-1].split('.')[0]) for f in files]
    n_raw = len(frame_indices)
    unsorted = []
    for i in tqdm(range(n_raw), desc='Validating raw data'):
        with h5py.File(files[i], 'r') as f:
            ind_sorted = np.lexsort((f['tag'][:,1], f['tag'][:,0]))
            increments = np.diff(ind_sorted).astype('int')

            if np.any(increments != 1):
                unsorted.append(i)

    if len(unsorted) > 0:
        sys.stdout.write('The following RAW files were found to be unsorted:\n')
        for i in unsorted:
            sys.stdout.write(f'{i}/{n_raw} -> {files[i]}\n')
    else:
        sys.stdout.write('All files have been sorted!\n')

def main():
    parser = argparse.ArgumentParser(
        prog='osiraws',
        description='Sort the raw particle data by particle id of a specified OSIRIS simulation.'
    )

    subparser = parser.add_subparsers()
    list_parser = subparser.add_parser('list')
    list_parser.add_argument('sim_dir',  help='Path to the OSIRIS simulation.')
    list_parser.set_defaults(func=list_routine)
    
    sort_parser = subparser.add_parser('sort')
    sort_parser.add_argument('sim_dir', help='Path to the OSIRIS simulation.')
    sort_parser.add_argument(
        '-s', 
        '--species',
        required=True, 
        help='Species name.'
    )

    sort_parser.add_argument(
        '-o',
        '--output',
        default=None,
        help='Destination folder of sorted raw data.'
    )
    sort_parser.add_argument(
        '--skip_copy',
        action='store_true',
        help='Flag over whether to skip copying the raw file tree.'
    )
    sort_parser.add_argument(
        '--start_at',
        default=None,
        type=int,
        help='Flag to specify the # raw file to start at (in case of overtime.)'
    )
    sort_parser.set_defaults(func=sort_routine)
    validate_parser = subparser.add_parser('validate')
    validate_parser.add_argument('raw_dir', help='Path to the RAW directory in question.')
    validate_parser.set_defaults(func=validate)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())
