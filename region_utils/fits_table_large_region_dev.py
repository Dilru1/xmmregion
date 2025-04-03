import os
import sys
import shutil
import pathlib
import numpy as np
from astropy.io import fits


def setup_paths(base_dir: str, obs_id: str):
    """
    Constructs and returns key paths used in the FITS table creation and region update.

    Parameters:
        base_dir (str): Base working directory.
        obs_id (str): Observation ID.

    Returns:
        dict: Dictionary containing all relevant paths.
    """
    data_path = pathlib.Path(base_dir).resolve() / 'data'
    return {
        'obsid': obs_id,
        'mypath': data_path,
        'save_path': data_path / 'final_reg_fits_table',
        'final_path': data_path / 'final_masks_fits',
        'base_file_path': data_path / 'reg_fits_table',
        'reg_files': data_path / 'reg_files',
        'fits_file_path': pathlib.Path(sys.argv[1]).resolve()
    }


def ensure_directories(paths):
    """
    Ensure required output directories exist.

    Parameters:
        paths (dict): Dictionary of path variables.
    """
    os.makedirs(paths['save_path'], exist_ok=True)
    os.makedirs(paths['final_path'], exist_ok=True)


def create_region_table(paths, fits_file, reg_file, base_reg_fit_file, instr):
    """
    Creates a new FITS region table based on a base template and region definitions.

    Parameters:
        paths (dict): Paths dictionary.
        fits_file (str): Input FITS file name.
        reg_file (str): Region definition file.
        base_reg_fit_file (str): Template FITS region file.
        instr (str): Instrument name.
    """
    hdu = fits.open(paths['fits_file_path'] / fits_file)[0]
    hdr_base = hdu.header

    row1 = np.array([line.strip() for line in open(paths['reg_files'] / reg_file)])
    row1 = np.delete(row1, [0, 1, 2])
    row_c = len(row1)

    hdul = fits.open(paths['base_file_path'] / base_reg_fit_file)
    table = hdul[1]
    hdr = table.header
    hdr0 = hdul[0].header
    mode = base_reg_fit_file[-8:-5]

    ntable = fits.BinTableHDU.from_columns(table.columns, nrows=row_c, fill=True)
    out_path = paths['final_path'] / f'box_table_{instr}_{mode}.fits'
    ntable.writeto(out_path, overwrite=True)
    hdul.close()

    hdul2 = fits.open(out_path, mode='update')
    hdr2 = hdul2[1].header
    hdr2_0 = hdul2[0].header

    # Copy standard headers
    for key in ['EXTNAME', 'HDUVERS', 'HDUCLASS', 'HDUCLAS1', 'HDUCLAS2', 'MTYPE1', 'MFORM1']:
        hdr2[key] = hdr[key]

    for key in ['XPROC0', 'XDAL0', 'CREATOR', 'DATE', 'LONGSTRN']:
        hdr2_0[key] = hdr0[key]

    for key in ['CTYPE1', 'CTYPE2', 'CRVAL1', 'CRVAL2', 'CRPIX1', 'CDELT1', 'CDELT2']:
        hdr2_0[key] = hdr_base[key]

    hdul2.close()


def update_region_table(paths, reg_file, base_reg_fit_file, instr):
    """
    Updates an existing region FITS table with parameters from a region file.

    Parameters:
        paths (dict): Dictionary of relevant paths.
        reg_file (str): Region file to read.
        base_reg_fit_file (str): Base FITS file used to derive mode.
        instr (str): Instrument name.
    """
    mode = base_reg_fit_file[-8:-5]
    hdul1 = fits.open(paths['final_path'] / f'box_table_{instr}_{mode}.fits', mode='update')
    table1 = hdul1[1]

    row1 = np.array([line.strip() for line in open(paths['reg_files'] / reg_file)])
    row1 = np.delete(row1, [0, 1, 2])

    for i, row in enumerate(row1):
        tokens = row[4:-1].split(',')
        x, y, r1, r2 = map(float, tokens[:4])
        ang = float(tokens[4]) if mode == 'det' else 301.28
        key_x, key_y = ('DETX', 'DETY') if mode == 'det' else ('X', 'Y')

        table1.data[i]['SHAPE'] = 'ROTBOX'
        table1.data[i][key_x][0] = x
        table1.data[i][key_y][0] = y
        table1.data[i]['R'][0] = r1
        table1.data[i]['R'][1] = r2
        table1.data[i]['ROTANG'][0] = ang
        table1.data[i]['COMPONENT'] = 1

    hdul1.close()


def copy_folder_contents(source_folder, destination_folder):
    """
    Copies all files and folders from a source to destination directory.

    Parameters:
        source_folder (Path): Source directory.
        destination_folder (Path): Destination directory.
    """
    os.makedirs(destination_folder, exist_ok=True)
    for item in os.listdir(source_folder):
        src = os.path.join(source_folder, item)
        dst = os.path.join(destination_folder, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)


if __name__ == "__main__":
    paths = setup_paths('.', '0203930101')
    ensure_directories(paths)

    fits_f = [
        'pnS003-obj-image-sky.fits',
        'mos1S001-obj-image-sky.fits',
        'mos2S002-obj-image-sky.fits'
    ]
    regions_det = ['box_mask_pn_det.reg', 'box_mask_m1_det.reg', 'box_mask_m2_det.reg']
    regions_sky = ['box_mask_pn_sky.reg', 'box_mask_m1_sky.reg', 'box_mask_m2_sky.reg']
    tables_det = ['pnS003-bkg_region-det.fits', 'mos1S001-bkg_region-det.fits', 'mos2S002-bkg_region-det.fits']
    tables_sky = ['pnS003-bkg_region-sky.fits', 'mos1S001-bkg_region-sky.fits', 'mos2S002-bkg_region-sky.fits']
    instrs = ['pn', 'm1', 'm2']

    for i in range(3):
        create_region_table(paths, fits_f[i], regions_det[i], tables_det[i], instrs[i])
        update_region_table(paths, regions_det[i], tables_det[i], instrs[i])

    for i in range(3):
        create_region_table(paths, fits_f[i], regions_sky[i], tables_sky[i], instrs[i])
        update_region_table(paths, regions_sky[i], tables_sky[i], instrs[i])

    copy_folder_contents(paths['final_path'], paths['fits_file_path'])