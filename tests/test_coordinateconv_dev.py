import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from io import StringIO
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from region_utils import coordinateconv_dev as coord


@pytest.fixture
def fake_reg_file(tmp_path):
    # Minimal dummy reg file
    reg_file = tmp_path / "reg_row_pix.reg"
    content = "\n".join([
        "# header",
        "global",
        "physical",
        "box(100.0,200.0,1.0,1.0,0)",
        "box(150.0,250.0,1.2,0.8,0)"
    ])
    reg_file.write_text(content)
    return reg_file


@pytest.fixture
def mock_fits(monkeypatch):
    class FakeWCS:
        def __init__(self, header=None):
            self.wcs = MagicMock(pc=np.array([[1.0, 0], [0, 1.0]]))  # identity rotation

        def all_pix2world(self, x, y, origin):
            return (x + 0.5, y + 0.5)

        def all_world2pix(self, x, y, origin):
            return (x - 0.5, y - 0.5)

    class FakeHDU:
        def __init__(self, header_data):
            self.header = header_data

    header_data = {
        "CRPIX1L": 1000,
        "CRPIX2L": 1000,
        "CRVAL1L": 10.0,
        "CRVAL2L": 20.0,
        "CDELT1L": 0.01,
        "CDELT2L": 0.01
    }

    monkeypatch.setattr(coord, "WCS", lambda h: FakeWCS())
    monkeypatch.setattr(coord.fits, "open", lambda path: [FakeHDU(header_data)])


def test_create_sky_maps(fake_reg_file, mock_fits, tmp_path):
    output = StringIO()
    coords = coord.create_sky_maps(
        reduced_reg_file=fake_reg_file,
        instrid="pnS003",
        outfile_1=output,
        save_path=tmp_path,
        maps_count_path=tmp_path
    )
    result = output.getvalue()
    assert "# Region file format" in result
    assert "box(" in result


def test_create_coordinate_conversion_files(fake_reg_file, mock_fits, tmp_path):
    out3 = StringIO()
    out4 = StringIO()
    out5 = StringIO()

    coord.create_coordinate_conversion_files(
        epoch="2004",
        reduced_reg_file=fake_reg_file,
        outfile3=out3,
        outfile4=out4,
        outfile5=out5,
        maps_count_path=tmp_path
    )

    assert "esky2det" in out3.getvalue()
    assert "pnS003" in out3.getvalue()


def test_create_coordinate_conversion_files_big(fake_reg_file, mock_fits, tmp_path):
    out6 = StringIO()

    coord.create_coordinate_conversion_files_big(
        epoch="2004",
        big_reg_file=fake_reg_file,
        outfile6=out6,
        maps_count_path=tmp_path
    )

    content = out6.getvalue()
    assert "esky2det" in content
    assert "pnS003" in content
    assert "mos1S001" in content
    assert "mos2S002" in content

