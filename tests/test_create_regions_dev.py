import tempfile
from pathlib import Path
import pytest
#import coordinateconv


from region_utils import coordinateconv_dev as  coordinateconv
from region_utils import create_regions_dev as create_regions


@pytest.fixture
def mock_coordinateconv(monkeypatch):
    # Create a dummy class to mock all coordinateconv functions
    class DummyCoord:
        @staticmethod
        def create_coordinate_conversion_files(epoch, path, out3, out4, out5, maps_count_path):
            out3.write("# dummy pn\n")
            out4.write("# dummy m1\n")
            out5.write("# dummy m2\n")

        @staticmethod
        def create_coordinate_conversion_files_big(epoch, path, out6, maps_count_path):
            out6.write("# dummy big\n")

        @staticmethod
        def create_sky_maps(input_path, instrument, outfile_1, save_path, maps_count_path):
            outfile_1.write(f"# dummy sky map for {instrument}\n")
            return [(123.45, 67.89, 90.0)]

    # Patch the coordinateconv module used inside create_regions
    monkeypatch.setattr(create_regions, "coordinateconv", DummyCoord)


def test_run_region_creation_success(mock_coordinateconv):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Run the main function
        ra, dec, theta = create_regions.run_region_creation("2004", tmp_path)

        # Assertions
        assert isinstance(ra, float)
        assert isinstance(dec, float)
        assert isinstance(theta, float)
        assert (tmp_path / "region_coord_pn.sh").exists()
        assert (tmp_path / "region_big.sh").exists()
        assert (tmp_path / "region_coord_m1.sh").exists()
        assert (tmp_path / "region_coord_m2.sh").exists()

        # Check a generated reg file
        reg_file = Path.cwd() / "data" / "reg_files" / "reg_sky_pn.reg"
        assert reg_file.exists()
        assert "dummy sky map" in reg_file.read_text()
