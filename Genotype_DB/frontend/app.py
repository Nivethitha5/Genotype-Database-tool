'''
import streamlit as st
import requests
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# -------------------------------
# PAGE CONFIG (important)
# -------------------------------
st.set_page_config(
    page_title="Acrannolife Genotyping LIMS",
    page_icon="🧬",
    layout="wide"
)

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
DB_URL = "postgresql://genouser:Acrannolifegenomics@localhost:5432/genotype_db"
engine = create_engine(DB_URL)

# -------------------------------
# HEADER
# -------------------------------
st.markdown(
    """
    <div class="lims-card">
        <h2>Acrannolife Genomics Pvt Ltd 🧬</h2>
        <p>Genotyping LIMS</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- GLOBAL CSS ----------
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: #f4f8fb;
    }

    /* Main container */
    .block-container {
        padding: 2rem;
    }

    /* Card-like boxes */
    .lims-card {
        border: 2px solid #2c7be5;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
    }

    /* Table borders */
    table {
        border-collapse: collapse !important;
        width: 100%;
    }

    th, td {
        border: 1px solid #2c7be5 !important;
        padding: 8px !important;
        text-align: center !important;
        font-size: 14px;
    }

    th {
        background-color: #e3f2fd;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.divider()

# -------------------------------
# FILE UPLOAD SECTION
# -------------------------------

st.subheader("📤 Upload QuantStudio Result File")

uploaded_file = st.file_uploader(
    "Accepted formats: .xlsx, .xls, .xlsm",
    type=["xlsx", "xls", "xlsm"]
)

if uploaded_file:
    st.success(f"Selected file: {uploaded_file.name}")

    if st.button("Upload & Store", use_container_width=True):
        with st.spinner("Uploading and processing file..."):
            response = requests.post(
                "http://127.0.0.1:8000/upload_quantstudio/",
                files={"file": uploaded_file}
            )

        if response.status_code == 200:
            st.success("✅ Upload successful!")
            st.json(response.json())
        else:
            st.error("❌ Upload failed")
            st.text(response.text)

st.divider()

# -------------------------------
# DATABASE VIEW SECTION
# -------------------------------
st.subheader("🧬 Sample × Probe Genotype Matrix")

try:
    geno_df = pd.read_sql(
        """
        SELECT patient_id, probe, genotype
        FROM genotypes
        WHERE patient_id <> 'NTC'
        """,
        engine
    )

    # Pivot table: rows = samples, columns = probes
    genotype_matrix = geno_df.pivot_table(
        index="patient_id",
        columns="probe",
        values="genotype",
        aggfunc="first"
    )

    st.dataframe(
        genotype_matrix,
        use_container_width=True,
        height=600
    )

except Exception as e:
    st.error("Failed to generate genotype matrix")
    st.text(str(e))
---------------------------------------------------------------------

import streamlit as st
import pandas as pd
import base64
import psycopg2

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Acrannolife Genotyping LIMS",
    layout="wide"
)

# -------------------------------------------------
# Load DNA image and convert to base64
# -------------------------------------------------
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

dna_base64 = get_base64_image("frontend/assets/dna_bg.png")

# -------------------------------------------------
# Global CSS (BACKGROUND + BORDERS + LAB STYLE)
# -------------------------------------------------
st.markdown(
    f"""
    <style>

    html, body, .stApp {{
        height: 100%;
        margin: 0;
    }}

    /* FULL PAGE DNA BACKGROUND */
    .stApp {{
        background:
            linear-gradient(
                rgba(248, 251, 255, 0.96),
                rgba(248, 251, 255, 0.96)
            ),
            url("data:image/png;base64,{dna_base64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
    }}

    /* MAIN CONTENT */
    .block-container {{
        padding: 2rem 3rem;
    }}

    /* CARD STYLE */
    .lims-card {{
        background: white;
        border: 1.5px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    }}

    /* TABLE HEADER FIX (VERY IMPORTANT) */
    thead th {{
        background-color: #1f2937 !important;
        color: #ffffff !important;
        font-weight: 600;
        text-align: center;
        border: 1px solid #d1d5db !important;
    }}

    tbody td {{
        border: 1px solid #e5e7eb !important;
        text-align: center;
        font-weight: 600;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    """
    <div class="lims-card">
        <h2>🧬 Acrannolife Genomics Pvt Ltd</h2>
        <p>Genotyping LIMS – QuantStudio SNP Analysis</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
conn = psycopg2.connect(
    host="localhost",
    database="genotype_db",
    user="genouser",
    password="Acrannolifegenomics"
)

# -------------------------------------------------
# DASHBOARD METRICS
# -------------------------------------------------
exp_count = pd.read_sql("SELECT COUNT(*) FROM experiments", conn).iloc[0, 0]
sample_count = pd.read_sql(
    "SELECT COUNT(DISTINCT patient_id) FROM genotypes WHERE patient_id != 'NTC'",
    conn
).iloc[0, 0]

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="card" style="text-align:center">
            <div class="metric">{exp_count}</div>
            <div class="metric-label">Total Experiments</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card" style="text-align:center">
            <div class="metric">{sample_count}</div>
            <div class="metric-label">Total Samples</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📤 Upload QuantStudio Results")

uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xls", "xlsx"]
)

if uploaded_file:
    st.success("File uploaded successfully ✔")
    st.info("Processing handled by backend API")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# GENOTYPE MATRIX
# -------------------------------------------------
st.markdown("<div class='lims-card'>", unsafe_allow_html=True)
st.subheader("🧪 Genotype Matrix")

query = """
SELECT patient_id, probe, genotype
FROM genotypes
WHERE patient_id != 'NTC'
ORDER BY patient_id, probe
"""

df = pd.read_sql(query, conn)

if not df.empty:
    matrix = df.pivot(index="patient_id", columns="probe", values="genotype")

    def style_cells(val):
        if val == "V/V":
            return "background-color: #d4edda"
        if val == "F/F":
            return "background-color: #d1ecf1"
        if val == "V/F":
            return "background-color: #f8d7da"
        return ""

    st.dataframe(
        matrix.style.applymap(style_cells),
        use_container_width=True,
        height=350
    )
else:
    st.warning("No genotype data found")

st.markdown("</div>", unsafe_allow_html=True)

conn.close()
-----------------------------------------------------
'''


import streamlit as st
import pandas as pd
import psycopg2
import base64
import requests
import os

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title="Acrannolife Genotyping LIMS",
    layout="wide"
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

logo_base64 = get_base64_image("frontend/assets/logo_2.png")
# --------------------------------------------------
# LOAD DNA BACKGROUND IMAGE
# --------------------------------------------------
def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

dna_base64 = load_base64_image("frontend/assets/dna_bg.png")

# --------------------------------------------------
# GLOBAL CSS (BACKGROUND + BORDERS + TABLE FIX)
# --------------------------------------------------
st.markdown(
    f"""
    <style>

    html, body, .stApp {{
        height: 100%;
        margin: 0;
    }}

    /* FULL BACKGROUND */
    .stApp {{
        background:
            linear-gradient(
                rgba(248, 251, 255, 0.8),
                rgba(248, 251, 255, 0.8)
            ),
            url("data:image/png;base64,{dna_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .block-container {{
        padding: 2rem 3rem;
    }}

    /* CARD STYLE */
    .lims-card {{
        background: #558ba8;
        border: 1.5px solid #2563eb;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    }}

    /* TABLE HEADER FIX */
    thead th {{
        background-color: #2b5896 !important;
        color: white !important;
        font-weight: 700;
        text-align: center;
        border: 1px solid #d1d5db !important;
    }}
    
    tbody td {{
        border: 1px solid #e5e7eb !important;
        text-align: center;
        font-weight: 600;
    }}

    [data-testid="stDataFrame"] div[role="columnheader"] {{
    background-color: #063b85 !important;
    color: white !important;
    font-weight: 700 !important;
    text-align: center !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(f"""
<style>
.header-container {{
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px;
    background: rgba(255,255,255,0.85);
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
}}

.header-container img {{
    height: 100px;
}}

.header-text {{
    display: flex;
    flex-direction: column;
}}

.header-title {{
    font-size: 45px;   /* Increased */
    font-weight: 800;
    color: #0d2b45;
    letter-spacing: 1px;
}}

.header-subtitle {{
    font-size: 23px;   /* Increased */
    color: #444;
    margin-top: 4px;
}}
</style>

<div class="header-container">
    <img src="data:image/png;base64,{logo_base64}">
    <div class="header-text">
        <div class="header-title">Acrannolife Genomics Pvt Ltd</div>
        <div class="header-subtitle">Genotyping Laboratory Tool</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
conn = psycopg2.connect(
    host="localhost",
    database="genotype_db",
    user="genouser",
    password="yourpassword"
)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    total_experiments = pd.read_sql(
        "SELECT COUNT(*) FROM experiments", conn
    ).iloc[0, 0]

    st.markdown(
        f"""
        <div class="lims-card" style="text-align:center">
            <h1>{total_experiments}</h1>
            <p>Total Experiments</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    total_samples = pd.read_sql(
        """
        SELECT COUNT(DISTINCT patient_id)
        FROM genotypes
        WHERE patient_id <> 'NTC'
        """,
        conn
    ).iloc[0, 0]

    st.markdown(
        f"""
        <div class="lims-card" style="text-align:center">
            <h1>{total_samples}</h1>
            <p>Total Samples</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# FILE UPLOAD SECTION
# --------------------------------------------------
st.subheader("📤 Upload New QuantStudio File")

uploaded_file = st.file_uploader(
    "Upload QuantStudio Results File",
    type=["xls", "xlsx"]
)

if uploaded_file:
    if st.button("Process & Upload"):
        with st.spinner("Processing..."):
            response = requests.post(
                "http://127.0.0.1:8000/upload_quantstudio/",
                files={"file": uploaded_file}
            )

        if response.status_code == 200:
            st.success("Upload Successful ✅")
            st.session_state["refresh_matrix"] = True
        else:
            st.error("Upload Failed ❌")

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# GENOTYPE MATRIX
# --------------------------------------------------
st.subheader("🧪 Genotype Matrix (Samples × Probes)")

query = """
SELECT patient_id, probe, genotype
FROM genotypes
WHERE patient_id <> 'NTC'
ORDER BY patient_id, probe
"""

df = pd.read_sql(query, conn)

matrix = df.pivot(
    index="patient_id",
    columns="probe",
    values="genotype"
)

if st.session_state.get("refresh_matrix", False):

    # Call backend to fetch updated matrix
    matrix_response = requests.get(
        "http://127.0.0.1:8000/get_genotype_matrix/"
    )

    if matrix_response.status_code == 200:
        geno_matrix = pd.DataFrame(matrix_response.json())
        # render styled matrix here
# --------------------------------------------------
# COLOR CODING
# --------------------------------------------------

def genotype_color(val):

    # Handle NaN or missing values
    if pd.isna(val) or val in ["-", "No Call", ""]:
        return "background-color: #ede9fe; color:  #5b21b6; font-weight: 600; border: 1px solid #f97316;"

    # V/V → Enhanced Green
    elif val == "V/V":
        return "background-color: #bbf7d0; color: #065f46; font-weight: 700; border: 1px solid #22c55e;"

    # F/F → Enhanced Blue
    elif val == "F/F":
        return "background-color: #bfdbfe; color: #1e3a8a; font-weight: 700; border: 1px solid #3b82f6;"

    # V/F → Enhanced Red
    elif val == "V/F":
        return "background-color: #fecaca; color: #7f1d1d; font-weight: 700; border: 1px solid #ef4444;"

    return ""

styled_matrix = (
    matrix
    .style
    .map(genotype_color)
    .set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#2b5896"),
                ("color", "white"),
                ("font-weight", "700"),
                ("text-align", "center"),
                ("border", "1px solid #374151"),
                ("padding", "20px"),
                ("font-size", "18px")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("text-align", "center"),
                ("border", "1px solid #e5e7eb"),
                ("padding", "20px"),
                ("font-size", "12px")
            ]
        },
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse"),
                ("width", "100vw")
            ]
        }
    ])
)

st.dataframe(
    styled_matrix,
    width='stretch'

)
