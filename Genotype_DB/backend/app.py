from fastapi import FastAPI, UploadFile, File
import pandas as pd
import uuid
import numpy as np

from backend.db import engine
from backend.genotype import call_genotype

app = FastAPI(title="Acrannolife Genotyping LIMS")

@app.get("/")
def health():
    return {"status": "Genotype LIMS running"}

@app.post("/upload_quantstudio/")
async def upload_quantstudio(file: UploadFile = File(...)):

    experiment_id = uuid.uuid4()

    # Read QuantStudio Results tab
    df = pd.read_excel(
        file.file,
        sheet_name="Results",
        header= 40

    )
    df = df[df["Sample Name"] != "NTC"].copy()
    
    ct_cols = ["Allele1 Ct", "Allele2 Ct"]

    for col in ct_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Create experiment record
    pd.DataFrame([{
        "experiment_id": experiment_id
    }]).to_sql(
        "experiments",
        engine,
        if_exists="append",
        index=False
    )

    # Auto genotype calling
    df["genotype_auto"] = df.apply(
    lambda r: call_genotype(
        r["Allele1 Delta Rn"],   # VIC
        r["Allele2 Delta Rn"],   # FAM
        r["Allele1 Ct"],         # VIC Ct
        r["Allele2 Ct"],         # FAM Ct
    ),
    axis=1
    )

    # -------------------------
    # Store RAW QuantStudio data
    # -------------------------
    raw_df = df.rename(columns={
        "Sample Name": "patient_id",
        "SNP Assay Name": "probe",
        "Allele1 Delta Rn": "allele1_delta_rn",
        "Allele2 Delta Rn": "allele2_delta_rn",
        "Allele1 Ct": "allele1_ct",
        "Allele2 Ct": "allele2_ct",
        "Quality(%)": "quality",
        "Call": "qs_call",
        "THOLDFAIL": "tholdcallfail"
    })


    raw_df["experiment_id"] = experiment_id

    raw_df[[
        "patient_id", "probe",
        "allele1_delta_rn", "allele2_delta_rn",
        "allele1_ct", "allele2_ct",
        "quality", "qs_call","tholdcallfail",
        "experiment_id"
    ]].to_sql(
        "raw_qpcr",
        engine,
        if_exists="append",
        index=False
    )

    # -------------------------
    # Store DERIVED genotypes
    # -------------------------
    geno_df = raw_df[["patient_id", "probe"]].copy()
    geno_df["genotype"] = df["genotype_auto"]
    geno_df["confidence"] = raw_df["quality"]
    geno_df["call_method"] = "DeltaRn_QC_Aware"
    geno_df["experiment_id"] = experiment_id

    geno_df.to_sql(
        "genotypes",
        engine,
        if_exists="append",
        index=False
    )

    return {
        "status": "SUCCESS",
        "experiment_id": str(experiment_id),
        "records_processed": len(df)
    }

@app.get("/get_genotype_matrix/")
def get_matrix():
    query = """
        SELECT patient_id, probe, genotype
        FROM genotypes
        WHERE patient_id != 'NTC'
    """

    df = pd.read_sql(query, engine)

    matrix = df.pivot(
        index="patient_id",
        columns="probe",
        values="genotype"
    )

    return matrix.fillna("").to_dict()
