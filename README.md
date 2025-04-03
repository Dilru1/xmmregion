# xmmregion Project

> A hybrid Bash-Python toolkit designed to streamline *diffuse X-ray* spectral extraction from complex and numerous X-ray regions in XMM-Newton observations.


## Overview

The **Science Analysis System (SAS)** of ESA’s **X-ray Multi-Mirror Mission (XMM-Newton)** is a collection of tasks, scripts, and libraries developed to reduce and analyze observational data. It is built using C, Fortran, and Perl. Within SAS, the **XMM-Newton Extended Source Analysis Software (XMM-ESAS)** is specifically designed to handle diffuse X-ray emission from various extended structures.

However, XMM-ESAS has a significant limitation: it cannot efficiently extract diffuse spectra from more than approximately 40 regions simultaneously. This becomes particularly challenging when working with complex, pixel-defined region files. The following image shows an example from the Galactic Center’s Sgr B region. In this case, the user aims to extract spectra from all non-black pixels (each representing a 30×30 arcsecond area on the sky), which is difficult to achieve using ESAS alone.


<p align="center">
  <img src="assets/image.png" alt="Region Map of Sgr B Galactic Center for different OBSID" width="400"/>
</p>


`xmmregion` is an automated toolkit developed to address this limitation. It streamlines the process of spectral extraction from a large number of region files (down to the pixel level) making it significantly easier to analyze spatially complex, extended X-ray sources. The toolkit is particularly useful in scenarios that require custom, pixel-by-pixel masking.



## Method

The standard XMM-Newton spectral extraction pipeline using XMM-ESAS must be **paused** before region based filtering begins. This is where `xmmregion` takes over, providing automated preprocessing to generate region files based on pixel level masks.

The workflow proceeds as follows:

1. **Pause Standard Pipeline**  
   Begin by stopping the standard XMM-Newton ESAS pipeline before region-based filtering starts (after `pn-filter` and `mos-filter`.

2. **Create a Binary Pixel Mask (FITS file)**  
   Generate a FITS image where each pixel has a value of `1` if it should be **excluded** from the spectral analysis.


3. **Convert to Sky and Detector Coordinates**  
   Convert this binary mask into Ds9 .reg files on XMM-Newton sky coordinates, and then into **detector coordinates**, while accounting for the orientation and rotation of the onboard EPIC cameras.

4. **Apply Geometric Transformations**  
   Use the `conv_reg` method to apply necessary camera rotations and transformations to align regions correctly in detector space.

5. **Translate to FITS Tables with Metadata**  
   Convert the region files (.reg) into special FITS tables that include relevant metadata needed by ESAS.

7. **Resume ESAS Pipeline**  
   Integrate the generated FITS region files into the standard ESAS workflow and continue spectral extraction as usual.


This modular approach allows users to define hundreds of regions based on pixel-level masks and automate their integration into ESAS without manual region creation or editing. For the moment only `box, rot-box` and `circular` regions are possible. 


---



## 🚀 Quick Start

### Clone the repository

```bash
git clone git@github.com:Dilru1/xmmregion.git
cd xmmregion
```

### Set up Python environment

```bash
python3 -m venv xmmvenv
source xmmvenv/bin/activate
pip install -r requirements.txt
```

### Run the project

```bash
./main.sh
```


Note: To run xmmregion successfully, you must have SAS (Science Analysis System) installed and configured on your system. Additionally, preprocessed XMM-Newton ODF (Observation Data Files) are required. If you don't have them, feel free to contact me at dilrushanka@gmail.com, and I’ll be happy to provide the necessary files.


---

## 📁 Project Structure

```
xmmregion/
├── data/                # Data directory
├── 020301020/           # Outputs directory
├── region_utils/        # Python scripts and modules
├── tests/               # Unit tests
├── xmmvenv/             # Python virtual environment
├── main.sh              # Entry point script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 📖 Running Tests

Run unit tests to verify project correctness:

```bash
source xmmvenv/bin/activate
python -m unittest discover tests
```
---

## 🌐 Documentation

- Detailed documentation available [here](https://Dilru1.github.io/xmmregion) (Alert: Work in progress !....)

---


## ⚖️ License

© Dehiwalage Don Dilruwan ©dilrushanka@gmail.com

