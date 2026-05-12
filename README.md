
## Installation

This project uses a conda environment to manage the Python version and required packages. Follow below steps to start

### 1. Clone the repository

```bash
git clone https://gitlab.cc-asp.fraunhofer.de/ise-bst/fluseeq/ma_ronit.git
cd ma_ronit
```
### 2. Create conda environment using environment.yml file
```bash
conda env create -f environment.yml
```

### 3. Activate the environment
```bash
conda activate env
```

### 4. Install the local project using pyproject.toml:
```bash
python -m pip install -e .
```

### 5. Running the Main Simulation Scripts

Simulation with characteristic lines
```bash
python src/models/MVV_GKM_simulation_charline.py
```

Simulation with characteristic maps
```bash
python src/models/MVV_GKM_simulation_charmap.py
```

Simulation with real compressor powers
```bash
python src/models/MVV_GKM_simulation_compressorP.py
```


# Simulation and Calibration of Large-Scale Heat Pumps Using Measurement Data

This repository contains the Python code, data processing scripts, TESPy models, calibration routines, and plotting scripts used for my master's thesis:

**Simulation and Calibration of Large-Scale Heat Pumps Using Measurement Data**

The work focuses on the modelling and calibration of a large-scale heat pump system using measurement data. The model is implemented in Python using [TESPy](https://tespy.readthedocs.io/), CoolProp, pandas, NumPy, Matplotlib, and scikit-learn.

## Project Overview

The main objective of this project is to simulate the offdesign operation of a large-scale heat pump and calibrate the model against measured plant data.

The project includes:

- TESPy-based heat pump cycle modelling
- Compressor characteristic map evaluation
- Offdesign simulation
- Calibration of compressor performance
- Comparison between simulated and measured COP
- Error analysis using metrics such as RMSE, MAPE, R², and residual plots
- Generation of figures and tables for thesis documentation

## Repository Structure

```text
ma_ronit/
│
├── data/process_data
│   ├── Manheim_data_original                 # Original measurement data
│   └── Manheim_data_cleaned                  # Cleaned and preprocessed data
│
├── results/            
│   └── *.csv                                 # Simulation and calibration outputs
│
├── src/
│   └── models/
│       ├── MVV_GKM_simulation_charmap.py       # Heat Pump simulation using char maps
│       ├── MVV_GKM_simulation_charline.py      # Heat Pump simulation using char lines
│       ├── MVV_GKM_simulation_compressorP.py   # Heat Pump simulation using real compressor Powers
|   └── plots/
│
|
│
├── pyproject.toml           # Python project configuration
├── environment.yml          # Conda environment file
└── README.md                # Project documentation