import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from region_utils import coordinateconv_dev as coordinateconv


def log(msg):
    print(f"[INFO] {msg}")


def init_paths(epoch: str, save_path: str):
    base_path = Path.cwd() / "data"
    save_path = Path(save_path)

    paths = {
        "maps_cut": base_path / "steady_maps",
        "maps_count": base_path / "count_maps",
        "reg_files": base_path / "reg_files",
        "reg_files_det": base_path / "reg_files_det",
        "save_path": save_path,
        "epoch": epoch,
    }

    for key in ["maps_cut", "maps_count", "reg_files", "reg_files_det"]:
        paths[key].mkdir(parents=True, exist_ok=True)

    return paths


def run_region_creation(epoch: str, save_path: str):
    possibilities = {"2000", "2004", "2012", "2018", "2020"}
    if epoch not in possibilities:
        raise ValueError("Epoch must be one of: 2000, 2004, 2012, 2018, 2020")

    paths = init_paths(epoch, save_path)
    reg_files = paths["reg_files"]
    save_path = paths["save_path"]

    print(reg_files, save_path)

    try:
        with open(save_path / "region_coord_pn.sh", "w") as out3, \
             open(save_path / "region_coord_m1.sh", "w") as out4, \
             open(save_path / "region_coord_m2.sh", "w") as out5:
            coordinateconv.create_coordinate_conversion_files(
                epoch,
                reg_files / "reg_row_pix.reg",
                out3,
                out4,
                out5,
                maps_count_path=paths["maps_count"]
            )

        with open(save_path / "region_big.sh", "w") as out6:
            coordinateconv.create_coordinate_conversion_files_big(
                epoch,
                reg_files / "box_mask_sky.reg",
                out6,
                maps_count_path=paths["maps_count"]
            )

        for instrid in ["pnS003", "mos1S001", "mos2S002"]:
            with open(reg_files / f"reg_sky_{instrid.split('S')[0].lower()}.reg", "w") as out:
                coordinateconv.create_sky_maps(
                    reg_files / "reg_row_pix.reg",
                    instrid,
                    outfile_1=out,
                    save_path=save_path,
                    maps_count_path=paths["maps_count"]
                )

        for instrid in ["pnS003", "mos1S001", "mos2S002"]:
            with open(reg_files / f"box_mask_{instrid.split('S')[0].lower()}_sky.reg", "w") as out:
                coord = coordinateconv.create_sky_maps(
                    reg_files / "box_mask_sky.reg",
                    instrid,
                    outfile_1=out,
                    save_path=save_path,
                    maps_count_path=paths["maps_count"]
                )

        log(f"Region coordinates: RA={coord[0][0]}, Dec={coord[0][1]}, Theta={coord[0][2]}")
        return coord[0][0], coord[0][1], coord[0][2]

    except IOError as e:
        raise RuntimeError(f"IO operation failed: {e.strerror}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python create_regions.py <EPOCH> <OUTPUT_PATH>")
        sys.exit(1)

    epoch = sys.argv[1]
    save_path = sys.argv[2]

    try:
        ra, dec, theta = run_region_creation(epoch, save_path)
        print(f"{ra} {dec} {theta}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()