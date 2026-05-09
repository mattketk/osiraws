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

def output_dir(args):
    out_path = args.output
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
    out = output_dir(args)
    sys.stdout.write('Selected species: ' + args.species+'\n')
    sys.stdout.write('Original directory: ' + orig+'\n')
    sys.stdout.write('Target directory: ' + out+'\n')
    copy_tree(orig, out)

    out = Path(out)
    files = [p for p in out.rglob('*.h5') if p.is_file()]
    file_prefix = f'RAW-{args.species}'
    frame_indices = [int(str(f).split('-')[-1].split('.')[0]) for f in sorted(files)]

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
    sort_parser.set_defaults(func=sort_routine)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())