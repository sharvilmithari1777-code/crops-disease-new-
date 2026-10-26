# Croplytics — Smart Agriculture Assistant 🌾🌱

**Croplytics** is a modern, responsive, full-stack agricultural decision-support web application designed for farmers, agronomists, and agricultural students. It combines machine-learning yield forecasting, leaf disease diagnostics, IPCC Tier 1 carbon accounting, and verified bio-inputs into a clean, modern interface.

---

## 🚀 Key Features & Modules

| Module | Core Functionality | Underlying Model / Scientific Engine | Status |
| :--- | :--- | :--- | :--- |
| **Plant Disease Detection** | Upload leaf images to diagnose foliar pathogens, symptoms, organic sprays, and chemical fungicides. | Optical feature extraction (Excess Green Index $ExG = 2G - R - B$, chlorosis & necrosis ratio) mapped to diagnostic pathology profiles. | **Demonstration Mode** (Transparent feature-based mock pipeline; PyTorch / TensorFlow CNN pluggable) |
| **Crop Yield Forecasting** | Predict harvest yield in tonnes/ha & total farm production across 10 major crops using soil N-P-K, pH, temperature, rain, and humidity. | **Trained Scikit-Learn Random Forest Regressor** ($R^2 > 0.98$, 100 estimators) calibrated with ICAR & FAO agronomic response curves. | **Genuine ML Model** (`models/crop_yield_model.joblib`) |
| **Carbon Footprint Calculator** | Measure farm greenhouse gas emissions (CO₂e) across fuel, electricity, fertilizer, and irrigation systems with Chart.js charts. | Official **IPCC Tier 1 Guidelines for National GHG Inventories**, DEFRA conversion factors, and Central Electricity Authority grid baselines. | **Documented Scientific Calculation** |
| **Product Recommendations** | Discover verified organic fertilizers, biofertilizers, composts, and mycorrhizae with application dosages. | Local agricultural catalog (`data/products.json`) with interactive search and category filtering. | **Advisory Catalog** (No commercial checkout) |
| **Authentication & History** | Secure user registration, login, session tracking, and audit logging of all farm scans. | SQLite database with **PBKDF2:SHA256 password hashing** via Werkzeug. | **Fully Functional Auth** |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10–3.12, Flask 3.1
- **Machine Learning**: Scikit-Learn, NumPy, Pandas, Joblib
- **Image Processing**: Pillow (PIL)
- **Database**: SQLite3 with Werkzeug Security
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Chart.js 4.4, Font Awesome 6.5
- **Platform**: Runs locally on Windows, macOS, or Linux

---

## 📂 Project Folder Structure

```
Croplytics/
│
├── app.py                     # Main Flask web application and route controllers
├── requirements.txt           # Python dependency specifications
├── START_HERE.bat             # 1-Click automatic launcher for Windows
├── README.md                  # Complete project documentation
│
├── models/
│   ├── README.md              # Machine learning architecture documentation
│   ├── train_yield_model.py   # Training script for Scikit-Learn model
│   └── crop_yield_model.joblib # Serialized trained Random Forest pipeline
│
├── services/
│   ├── __init__.py
│   ├── database.py            # SQLite schema, user auth, and activity logging
│   ├── disease_detection.py   # Leaf image inspection & demonstration pipeline
│   ├── yield_prediction.py    # ML inference and agronomic advisory engine
│   └── carbon_calculator.py   # Documented IPCC farm carbon accounting
│
├── data/
│   ├── emission_factors.json  # Documented IPCC Tier 1 & DEFRA emission factors config
│   ├── products.json          # Bio-inputs and agricultural product database
│   └── sample_leaf_data.json  # Plant disease pathology profiles and treatments
│
├── templates/
│   ├── base.html              # Modern responsive navbar, flash alerts, and footer
│   ├── index.html             # Homepage with hero, 4 cards, workflow, and benefits
│   ├── dashboard.html         # Farmer command center with stats and activity logs
│   ├── disease_detection.html # Leaf upload dropzone, preview, and treatment tabs
│   ├── yield_forecast.html    # 10-factor agronomic form, presets, and Chart.js
│   ├── carbon_calculator.html # Emissions calculator with Doughnut & Bar charts
│   ├── products.html          # Product catalog with search and modals
│   ├── login.html             # User authentication sign in
│   ├── register.html          # User registration with farm profile
│   └── history.html           # Full historical audit records
│
├── static/
│   ├── css/
│   │   └── style.css          # Curated green-and-white agricultural theme
│   ├── js/
│   │   └── main.js            # Image previews, Chart.js, presets, and filters
│   └── images/
│       └── samples/           # Built-in demonstration leaf sample images
│
└── uploads/                   # Dedicated directory for user-uploaded leaf photos
```

---

## ⚡ Quick Start on Windows (1-Click Setup)

The easiest way to run Croplytics on Windows:

1. Double-click the file **`START_HERE.bat`** in the project folder.
2. The batch script automatically:
   - Verifies that Python is installed.
   - Creates a virtual environment (`.venv`) if one does not exist.
   - Activates the virtual environment.
   - Installs all dependencies from `requirements.txt` (only on first launch).
   - Verifies or trains the Scikit-Learn Random Forest model (`models/crop_yield_model.joblib`).
   - Launches the Flask web server on `http://127.0.0.1:5000`.
   - Automatically opens your default web browser to the homepage.

---

## 💻 Manual Setup & Execution (Windows / Mac / Linux)

If you prefer to run manual commands in Command Prompt, PowerShell, or Terminal:

### 1. Prerequisites
Ensure you have **Python 3.10, 3.11, or 3.12** installed. Check with:
```bash
python --version
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Train the Crop Yield ML Model (If not already trained)
```bash
python models/train_yield_model.py
```
*Outputs evaluation metrics: $R^2 \approx 0.988$, $\text{RMSE} \approx 1.91$ tonnes/ha.*

### 5. Start the Web Server
```bash
python app.py
```

### 6. Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Demonstration vs. Genuine Models Disclosure

As per transparent engineering standards:

1. **Crop Yield Forecasting (Genuine Machine Learning)**:
   - **Algorithm**: `RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42)` trained via Scikit-Learn.
   - **Evaluation Metrics**: Tested on a 20% held-out test dataset with measured $R^2 = 0.9877$ ($R^2 \approx 0.988$) and $\text{RMSE} = 1.9147\text{ tonnes/ha}$.
   - **Dataset Disclosure**: Trained on a **simulated agronomic response dataset** calibrated against empirical biological benchmarks from the Indian Council of Agricultural Research (ICAR) and UN FAO. Integrates Mitscherlich-Baule diminishing nutrient returns and crop-specific thermal/pH tolerance bands.
   - **Consistency**: Both `models/train_yield_model.py` and `services/yield_prediction.py` share exact feature sequences (`crop_type`, `region`, `N`, `P`, `K`, `ph`, `temperature`, `rainfall`, `humidity`) and preprocessing pipelines.

2. **Carbon Footprint Calculator (Documented Mathematical Engineering)**:
   - Factors are decoupled into [`data/emission_factors.json`](file:///c:/Users/sharv/Downloads/APC/data/emission_factors.json) with documented scopes, units, and literature citations.
   - Official conversion factors:
     - Diesel: $2.68 \text{ kg CO}_2\text{e / L}$ (Scope 1 direct combustion, IPCC Energy Vol 2)
     - Grid Electricity: $0.82 \text{ kg CO}_2\text{e / kWh}$ (Scope 2 indirect pumping power, CEA baseline)
     - Synthetic Nitrogen Fertilizer: $4.96 \text{ kg CO}_2\text{e / kg}$ (Unified Haber-Bosch $2.10\text{ kg} + \text{Tier 1 direct soil nitrification } 2.86\text{ kg}$ to prevent double-counting)
     - Pesticides: $11.50 \text{ kg CO}_2\text{e / kg}$ active ingredient (Lal, R. 2004)
     - Irrigation methods: Micro-irrigation reduces baseline pumping overhead by 35–45%.
   - Results are explicitly presented as **illustrative engineering estimates** with documented limitations.

3. **Plant Disease Detection (Demonstration Mode)**:
   - Operates in a clearly labeled **Demonstration Mode**; heuristic optical feature extraction is never presented as a certified clinical diagnosis.
   - Evaluates Excess Greenness ($ExG = 2G - R - B$), yellow chlorosis, and dark necrosis ratios using Pillow and NumPy, deterministically mapped to calibrated pathology profiles.
   - **Safety Advisory Notice**: Prominently warns farmers to consult accredited agronomists, extension officers, or Krishi Vigyan Kendra (KVK) specialists before purchasing or spraying any chemical pesticides or fungicides.
   - A drop-in upgrade hook is documented in `models/README.md` and `services/disease_detection.py` for integrating a PyTorch or TensorFlow CNN (e.g. MobileNetV2 or ResNet-50) without modifying UI templates.

---

## 🔧 Troubleshooting Common Errors

### 1. `Python is not recognized as an internal or external command`
- **Cause**: Python was not added to your Windows system PATH during installation.
- **Fix**: Re-run the Python Windows installer, select **Modify**, and check the box **"Add Python to PATH"**.

### 2. `Port 5000 is already in use`
- **Cause**: Another service or previous Flask instance is occupying port 5000.
- **Fix**: You can close other terminal instances or modify the port in `app.py`:
  ```python
  app.run(host="127.0.0.1", port=5001, debug=True)
  ```

### 3. Image Upload Fails with File Size Error
- **Cause**: The application limits uploads to 5MB to conserve server resources and maintain speed.
- **Fix**: Compress or resize your photograph, or click one of the built-in 1-click demonstration leaf samples on the page.

---

## 📜 Academic Attribution & License
Created as an open-source educational project for smart, sustainable agriculture.
Free for college demonstration, coursework, and community development.
