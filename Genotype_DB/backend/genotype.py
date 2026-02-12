import pandas as pd
import numpy as np

def call_genotype(
    vic_delta_rn,
    fam_delta_rn,
    vic_ct,
    fam_ct,
    delta_threshold=0.5,
    ct_threshold=35
):

    # Convert safely to numeric (handles Undetermined, None, NaN)
    vic_delta_rn = pd.to_numeric(vic_delta_rn, errors="coerce")
    fam_delta_rn = pd.to_numeric(fam_delta_rn, errors="coerce")
    vic_ct = pd.to_numeric(vic_ct, errors="coerce")
    fam_ct = pd.to_numeric(fam_ct, errors="coerce")

    # ----------------------------------------------------
    # 🔴 1️⃣ BOTH Ct missing → No amplification
    # ----------------------------------------------------
    if pd.isna(vic_ct) and pd.isna(fam_ct):
        return "-"

    # ----------------------------------------------------
    # 🟡 2️⃣ Determine signal presence
    # ----------------------------------------------------
    vic_present = (
        pd.notna(vic_delta_rn)
        and vic_delta_rn >= delta_threshold
        and pd.notna(vic_ct)
        and vic_ct <= ct_threshold
    )

    fam_present = (
        pd.notna(fam_delta_rn)
        and fam_delta_rn >= delta_threshold
        and pd.notna(fam_ct)
        and fam_ct <= ct_threshold
    )

    # ----------------------------------------------------
    # 🟢 3️⃣ Genotype logic
    # ----------------------------------------------------
    if vic_present and fam_present:
        return "V/F"
    elif vic_present:
        return "V/V"
    elif fam_present:
        return "F/F"
    else:
        return "-"
