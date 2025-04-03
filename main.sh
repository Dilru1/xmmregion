#!/bin/bash

# Exit immediately on error, unset variables, or pipefail
set -euo pipefail
trap 'echo "[ERROR] Script failed at line $LINENO"; exit 1' ERR

# === Logging Functions ===
log() { echo -e "\033[1;34m[INFO]\033[0m $(date +'%Y-%m-%d %H:%M:%S') - $*"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; }


# === Argument Validation ===
if [[ $# -lt 2 ]]; then
    error "Usage: $0 <OBS_ID> <EPOCH>"
    exit 1
fi

id="$1"
epoch="$2"

id="0203930101"
epoch="2004"

export WORKDIR="$(pwd)"
export ANAPATH="$WORKDIR"

cd $ANAPATH


# === Configurable Paths ===
WORKDIR="$(pwd)"
ANAPATH="$WORKDIR"

#PFILES_BASE="/remote/pfiles/location"
#CALDB_PATH="/remote/$BASEDIR/sasfiles"

obsid="$id"
export ANAPATH WORKDIR obsid

# ==== XMM-Newton Path Variables ==== 
#export PFILES="$PFILES_BASE/$id"
#export SAS_CCFPATH="$CALDB_PATH/ccf"
#export CALDB="$CALDB_PATH/caldb_esas"
#export SAS_CCF="$ANAPATH/$obsid/ccf.cif"
#export SAS_ODF="$DATAPATH/$obsid/"
#export MY_ODF="$DATAPATH/$obsid/"

echo $epoch
echo $ANAPATH/$obsid

# === Initial Setup ===
log "Starting spectral analysis"
log "ObsID: $obsid | Epoch: $epoch"

mkdir -p "$ANAPATH/$obsid"
cd "$ANAPATH/$obsid"
rm -f *.dat *.txt

# === Dummy ODF File ===
export SAS_ODF="$(pwd)/$(ls -1 *SUM.SAS 2>/dev/null | head -n 1 || true)"
if [[ -z "$SAS_ODF" ]]; then
    warn "No SUM.SAS file found — using dummy file"
    export SAS_ODF="dummy_SUM.SAS"
fi


# === Python Region Creator ===
run_region_creation() {
    mkdir -p "$WORKDIR"
    cd "$WORKDIR"
    log "Running Python region script"

    output=$(python3 "$WORKDIR/region_utils/create_regions_dev.py" "$epoch" "$ANAPATH/$obsid" | grep -Eo '[+-]?[0-9]+([.][0-9]+)? [+-]?[0-9]+([.][0-9]+)? [+-]?[0-9]+([.][0-9]+)?')

    if [[ -z "$output" ]]; then
        error "No valid coordinates returned from create_regions.py"
        exit 1
    fi



    read -r ra dec theta <<< "$output"
    log "RA: $ra, Dec: $dec, Theta: $theta"
}



# === Region File Conversion ===
convert_regions() {
    cd "$ANAPATH/$obsid"
    for instrument in pnS003 mos1S001 mos2S002; do
        conv_reg mode=3 imagefile="${instrument}-obj-image-sky.fits" ra="$ra" dec="$dec" shape=ELLIPSE semimajor=0.1 semiminor=0.1 rotangle="$theta" >> angle.txt
    done
}

# === Run Source Scripts ===
run_sources() {
    source region_coord_pn.sh
    source region_coord_m1.sh
    source region_coord_m2.sh
    source region_big.sh
}

# === Copy Files ===
copy_outputs() {
    local dest="$WORKDIR/reg_files_det"
    mkdir -p "$dest"
    cp "$ANAPATH/$obsid"/*.txt "$dest"
    cp "$ANAPATH/$obsid"/*.dat "$dest"
    log "Copied region outputs to $dest"
}

# === Final Python and Shell Processing ===
final_processing() {
    cd "$WORKDIR"
    python3 region_utils/coordinate_conversions_dev.py "$ANAPATH/$obsid"
    python3 region_utils/fits_tables_single_pixels_dev.py "$ANAPATH/$obsid"
    python3 region_utils/fits_table_large_region_dev.py "$ANAPATH/$obsid"

    #cp pn_commands.sh "$ANAPATH/$obsid"
    #cp mos1_comands.sh "$ANAPATH/$obsid"
    #cp mos2_commands.sh "$ANAPATH/$obsid"

    cd "$ANAPATH/$obsid"
    #source "$WORKDIR/ssl_esas_analysis_mosa.sh"

    log "Analysis complete for ObsID $obsid"
    log "Current path: $(pwd)"
}

# === MAIN WORKFLOW ===
run_region_creation
#convert_regions
#run_sources
#copy_outputs
final_processing
