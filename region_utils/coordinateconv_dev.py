import os
import shutil
from math import acos, degrees
from pathlib import Path
import sys
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

def copy_files_with_extension(source_folder, destination_folder, extension):
    """
    Copies all files with a given extension from source to destination.
    """
    os.makedirs(destination_folder, exist_ok=True)
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        if os.path.isfile(item_path) and item.endswith(extension):
            shutil.copy2(item_path, destination_folder)

def create_sky_maps(reduced_reg_file, instrid, outfile_1, save_path, maps_count_path):
    """
    Generate DS9 region files from input reg file using WCS coordinates.
    """
    row = np.array([line.strip() for line in open(reduced_reg_file, 'r')])
    row = np.delete(row, [0, 1, 2])

    hdu = fits.open(Path(save_path) / f"{instrid}-obj-image-sky.fits")[0].header
    w = WCS(hdu)

    hdu2 = fits.open(Path(maps_count_path) / "count_map_2004.fits")[0]
    w2 = WCS(hdu2.header)

    theta_radians = acos(w2.wcs.pc[0, 0])
    theta_degrees = 360 - degrees(theta_radians)

    ref_x1 = hdu['CRPIX1L']
    ref_y1 = hdu['CRPIX2L']
    ref_x_val1 = hdu['CRVAL1L']
    ref_y_val1 = hdu['CRVAL2L']
    ref_x_inc1 = hdu['CDELT1L']
    ref_y_inc1 = hdu['CDELT2L']

    outfile_1.write('# Region file format: DS9 version 4.1\n')
    outfile_1.write(
        'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" '
        'select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n'
    )
    outfile_1.write('physical\n')

    coordinates = []

    for rr in row:
        try:
            d = rr[4:-1].split(',')
            coord1, coord2 = float(d[0]), float(d[1])
            coord3, coord4 = float(d[2]) * 600, float(d[3]) * 600

            if coord3 > 15000 and coord4 > 15000:
                coord3 = float(d[2]) * 600
                coord4 = float(d[3]) * 600

            X, Y = w2.all_pix2world(coord1, coord2, 1)

            if Path(reduced_reg_file).name.endswith('box_mask_sky.reg'):
                coordinates.append((X, Y, theta_degrees))

            mypix_x, mypix_y = w.all_world2pix(X, Y, 1)

            pix_value_x1 = round(ref_x_val1 + (mypix_x - ref_x1) * ref_x_inc1, 3)
            pix_value_y1 = round(ref_y_val1 + (mypix_y - ref_y1) * ref_y_inc1, 3)

            outfile_1.write(f"box({pix_value_x1},{pix_value_y1},{coord3},{coord4},{theta_degrees})\n")

        except ValueError:
            continue

    if Path(reduced_reg_file).name.endswith('box_mask_sky.reg'):
        return coordinates

def create_coordinate_conversion_files(epoch, reduced_reg_file, outfile3, outfile4, outfile5, maps_count_path):
    """
    Generate conversion command lines from reg file to coordinate scripts.
    """
    row = np.array([line.strip() for line in open(reduced_reg_file, 'r')])
    row = np.delete(row, [0, 1, 2])

    hdu = fits.open(Path(maps_count_path) / f"count_map_{epoch}.fits")[0]
    w = WCS(hdu.header)

    for rr in row:
        try:
            d = rr[4:-1].split(',')
            coord1, coord2 = float(d[0]), float(d[1])
            X, Y = w.all_pix2world(coord1, coord2, 1)

            outfile3.write(
                f"esky2det datastyle=user ra={X} dec={Y} outunit=det withheader=no "
                "calinfostyle=set calinfoset=pnS003-obj-image-sky.fits >> reg_pn.dat\n"
            )
            outfile4.write(
                f"esky2det datastyle=user ra={X} dec={Y} outunit=det withheader=no "
                "calinfostyle=set calinfoset=mos1S001-obj-image-sky.fits >> reg_mos1.dat\n"
            )
            outfile5.write(
                f"esky2det datastyle=user ra={X} dec={Y} outunit=det withheader=no "
                "calinfostyle=set calinfoset=mos2S002-obj-image-sky.fits >> reg_mos2.dat\n"
            )
        except ValueError:
            continue

def create_coordinate_conversion_files_big(epoch, big_reg_file, outfile6, maps_count_path):
    """
    Generate conversion commands for big region boxes.
    """
    row = np.array([line.strip() for line in open(big_reg_file, 'r')])
    row = np.delete(row, [0, 1, 2])

    hdu = fits.open(Path(maps_count_path) / f"count_map_{epoch}.fits")[0]
    w = WCS(hdu.header)

    for rr in row:
        try:
            d = rr[4:-1].split(',')
            coord1, coord2 = float(d[0]), float(d[1])
            X, Y = w.all_pix2world(coord1, coord2, 1)

            for cal in ["pnS003", "mos1S001", "mos2S002"]:
                outfile6.write(
                    f"esky2det datastyle=user ra={X} dec={Y} outunit=det withheader=no "
                    f"calinfostyle=set calinfoset={cal}-obj-image-sky.fits >> reg_box1.txt \n"
                )

        except ValueError:
            continue
