# xmmregion Project

> A hybrid Bash-Python toolkit designed to streamline *diffuse X-ray* spectral extraction from complex and numerous X-ray regions in XMM-Newton observations.


## Overview

The **Science Analysis System (SAS)** of ESA’s **X-ray Multi-Mirror Mission (XMM-Newton)** is a collection of tasks, scripts, and libraries developed to reduce and analyze observational data. It is built using C, Fortran, and Perl. Within SAS, the **XMM-Newton Extended Source Analysis Software (XMM-ESAS)** is specifically designed to handle diffuse X-ray emission from various extended structures.

However, XMM-ESAS has a significant limitation: it cannot efficiently extract diffuse spectra from more than approximately 40 regions simultaneously. This becomes particularly challenging when working with complex, pixel-defined region files. The following image shows an example from the Galactic Center’s Sgr B region. In this case, the user aims to extract spectra from all non-black pixels (each representing a 30×30 arcsecond area on the sky), which is difficult to achieve using ESAS alone.


<p align="center">
  <img src="assets/image.png" alt="Region Map of Sgr B Galactic Center for different OBSID" width="400"/>
</p>



`xmmregion` is a dedicated Python module created to address this limitation. It automates the process of spectral extraction from a large number of region files, making it significantly easier to analyze spatially complex, extended X-ray sources. It is especially useful for cases where custom, pixel-by-pixel masking is required.


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

## 📖 Detailed Usage

### Running Tests

Run unit tests to verify project correctness:

```bash
source xmmvenv/bin/activate
python -m unittest discover tests
```

### Customizing Inputs

Data files can be placed or updated inside `data/`.

### Outputs

Outputs are stored in `020301020/` after running `./main.sh`.

---

## 🌐 Documentation

- Detailed documentation available [here](https://Dilru1.github.io/xmmregion)

---

## 🛠 Contributing

Contributions are welcome!

1. Fork this repository
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push your changes: `git push origin feature-name`
5. Open a pull request

---

## ⚖️ License

MIT © Your Name

