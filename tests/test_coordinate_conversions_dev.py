import pytest
import tempfile
from pathlib import Path
import numpy as np

from region_utils import coordinate_conversions_dev as cc


@pytest.fixture
def temp_paths(tmp_path):
    """Set up temporary project structure and return paths dict."""
    (tmp_path / "data/steady_maps").mkdir(parents=True)
    (tmp_path / "data/count_maps").mkdir()
    (tmp_path / "data/reg_files").mkdir()
    (tmp_path / "data/reg_files_det").mkdir()

    obs_id = "0203930101"
    return cc.setup_paths(tmp_path, obs_id)


def write_dummy_region_file(path, content):
    with open(path, "w") as f:
        f.writelines(content)


def test_create_region_files_det(temp_paths):
    # Setup dummy inputs
    angle_file = temp_paths["reg_files_det"] / "angle.txt"
    write_dummy_region_file(angle_file, ["ELLIPSE 0 0 0 0 45.0\n"])

    row_pix_file = temp_paths["reg_files"] / "reg_row_pix.reg"
    write_dummy_region_file(row_pix_file, [
        "# Region file\n", "some header\n", "physical\n", "box(1.1,2.2,3,3,0)\n"
    ])

    coord_file = temp_paths["reg_files_det"] / "reg_pn.dat"
    write_dummy_region_file(coord_file, ["100.0 200.0\n", "150.0 250.0\n"])

    # Run the function
    cc.create_region_files_det(temp_paths, coord_file, "pn")

    output_file = temp_paths["reg_files"] / "reg_det_pn.reg"
    assert output_file.exists()
    contents = output_file.read_text()
    assert "box(100.0" in contents


def test_create_box_region_files_det(temp_paths):
    # Setup dummy inputs
    angle_file = temp_paths["reg_files_det"] / "angle.txt"
    write_dummy_region_file(angle_file, ["ELLIPSE 0 0 0 0 30.0\n", "ELLIPSE 0 0 0 0 60.0\n", "ELLIPSE 0 0 0 0 90.0\n"])

    sky_file = temp_paths["reg_files"] / "box_mask_sky.reg"
    write_dummy_region_file(sky_file, [
        "# Region file\n", "some header\n", "physical\n", "box(1.0,2.0,3.0,4.0,0)\n"
    ])

    coord_file = temp_paths["reg_files_det"] / "reg_box1.txt"
    write_dummy_region_file(coord_file, ["500.0 600.0\n", "700.0 800.0\n", "900.0 1000.0\n"])

    # Run function for each instrument
    for instr in ["pn", "m1", "m2"]:
        cc.create_box_region_files_det(temp_paths, coord_file, instr, sky_file)
        output = temp_paths["reg_files"] / f"box_mask_{instr}_det.reg"
        assert output.exists()
        assert "box(" in output.read_text()

    reg_m2_txt = temp_paths["reg_files"] / "reg_m2.txt"
    assert reg_m2_txt.exists()
    assert "circle(" in reg_m2_txt.read_text()
