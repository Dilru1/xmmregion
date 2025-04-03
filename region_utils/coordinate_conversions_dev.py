import numpy as np
import math
import random
import pathlib
import os
import re
import sys
from astropy.io import fits

def setup_paths(base_dir: str, obs_id: str):
    """
    Constructs and returns a dictionary of standardized paths used in the analysis.

    Parameters:
        base_dir (str): Base directory where data and analysis folders reside.
        obs_id (str): Observation ID (used to create output save path).

    Returns:
        dict: Dictionary of key paths (data, maps, region files, etc.).
    """
    base_path = pathlib.Path(base_dir).resolve()
    data_path = base_path / 'data'
    return {
        'basepath': base_path,
        'obsid': obs_id,
        'mypath': data_path,
        'maps_cut': data_path / 'steady_maps',
        'maps_count': data_path / 'count_maps',
        'reg_files': data_path / 'reg_files',
        'reg_files_det': data_path / 'reg_files_det',
        'save_path': base_path / obs_id
    }

def create_region_files_det(paths, eccord_file, instr, row_count_file=None):
    """
    Creates detector coordinate region files for a given instrument.

    Parameters:
        paths (dict): Dictionary containing necessary directory paths.
        eccord_file (Path): File path containing DETX, DETY coordinates.
        instr (str): Instrument name ('pn', 'm1', or 'm2').
        row_count_file (Path, optional): Path to pixel region definition file.
    """
    reg_files = paths['reg_files']
    reg_files_det = paths['reg_files_det']
    row_count_file = row_count_file or reg_files / 'reg_row_pix.reg'

    angle_file = reg_files_det / 'angle.txt'
    with open(angle_file, 'r') as file:
        file_content = file.read()
    pattern = r'\bELLIPSE\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)'
    angle_values = [float(m) for m in re.findall(pattern, file_content)]

    row2 = np.atleast_1d(np.loadtxt(row_count_file, dtype=str, skiprows=3))

    detx_dety_values = []
    with open(eccord_file, 'r') as file:
        for line in file:
            try:
                detx, dety = map(float, line.split())
                detx_dety_values.append((detx, dety))
            except ValueError:
                continue

    temp_path = reg_files / f'reg_{instr}_temp.reg'
    with open(temp_path, 'w') as df:
        for detx, dety in detx_dety_values:
            df.write(f'box({detx},{dety},600,600,0)\n')

    row3 = np.atleast_1d(np.loadtxt(temp_path, dtype=str))
    output_file = reg_files / f'reg_det_{instr}.reg'
    with open(output_file, 'w') as df2:
        df2.write('# Region file format: DS9 version 4.1\n')
        df2.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" '
                  'select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
        df2.write('detector\n')

        for box_par, box_info in zip(row2, row3):
            box_dim = int(box_par[4:-1].split(',')[2]) * 12 * 50
            box_coord_x = round(float(box_info[4:-1].split(',')[0]), 3)
            box_coord_y = round(float(box_info[4:-1].split(',')[1]), 3)
            angle = angle_values[1] if instr == 'm1' else angle_values[0]
            df2.write(f'box({box_coord_x},{box_coord_y},{box_dim},600,{angle})\n')

    os.remove(temp_path)

def create_box_region_files_det(paths, eccord_file, instr, row_count_file):
    """
    Creates detector coordinate box region files from box_mask sky definitions.

    Parameters:
        paths (dict): Dictionary containing necessary directory paths.
        eccord_file (Path): File with DETX, DETY coordinates.
        instr (str): Instrument name ('pn', 'm1', 'm2').
        row_count_file (Path): Input file with sky region box definitions.
    """
    reg_files = paths['reg_files']
    reg_files_det = paths['reg_files_det']

    angle_file = reg_files_det / 'angle.txt'
    with open(angle_file, 'r') as file:
        file_content = file.read()
    pattern = r'\bELLIPSE\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)'
    angle_values = [float(m) for m in re.findall(pattern, file_content)]

    row2 = np.atleast_1d(np.loadtxt(row_count_file, dtype=str, skiprows=3))
    dim_pattern = r"box\(\d+\.\d+,\d+\.\d+,(\d+\.\d+),(\d+\.\d+),"
    dim_values = [
        (float(m.group(1)) * 12 * 50, float(m.group(2)) * 12 * 50)
        for item in row2 if (m := re.search(dim_pattern, item))
    ]

    detx_dety_values = []
    with open(eccord_file, 'r') as file:
        for line in file:
            try:
                detx, dety = map(float, line.split())
                detx_dety_values.append((detx, dety))
            except ValueError:
                continue

    if instr not in {'pn', 'm1', 'm2'}:
        raise ValueError("Instrument not recognized.")

    idx = {'pn': 0, 'm1': 1, 'm2': 2}[instr]
    ang = angle_values[idx]
    output_path = reg_files / f'box_mask_{instr}_det.reg'

    with open(output_path, 'w') as df:
        df.write('# Region file format: DS9 version 4.1\n')
        df.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" '
                  'select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
        df.write('detector\n')
        df.write(f'box({detx_dety_values[idx][0]},{detx_dety_values[idx][1]},'
                 f'{dim_values[0][0]},{dim_values[0][1]},{ang})\n')

    if instr == 'm2':
        with open(reg_files / f'reg_{instr}.txt', 'w') as df:
            df.write(f'&&((DETX,DETY) IN circle({detx_dety_values[2][0]},'
                     f'{detx_dety_values[2][1]},450)')

if __name__ == "__main__":
    obs_id = '0203930101'
    paths = setup_paths('.', obs_id)

    create_region_files_det(paths, paths['reg_files_det'] / 'reg_pn.dat', 'pn')
    create_region_files_det(paths, paths['reg_files_det'] / 'reg_mos1.dat', 'm1')
    create_region_files_det(paths, paths['reg_files_det'] / 'reg_mos2.dat', 'm2')

    create_box_region_files_det(paths, paths['reg_files_det'] / 'reg_box1.txt', 'pn', paths['reg_files'] / 'box_mask_sky.reg')
    create_box_region_files_det(paths, paths['reg_files_det'] / 'reg_box1.txt', 'm1', paths['reg_files'] / 'box_mask_sky.reg')
    create_box_region_files_det(paths, paths['reg_files_det'] / 'reg_box1.txt', 'm2', paths['reg_files'] / 'box_mask_sky.reg')
