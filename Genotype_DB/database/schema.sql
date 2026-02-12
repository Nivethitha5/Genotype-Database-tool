CREATE TABLE patients (
    patient_id VARCHAR PRIMARY KEY
);

CREATE TABLE Probes (
    probe VARCHAR PRIMARY KEY
);

CREATE TABLE experiments (
    experiment_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_qpcr (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR,
    probe VARCHAR,
    allele1_delta_rn FLOAT,
    allele2_delta_rn FLOAT,
    allele1_ct FLOAT,
    allele2_ct FLOAT,
    quality FLOAT,
    qs_call TEXT,
    amp_nc TEXT,
    noise TEXT,
    tholdcallfail TEXT,
    experiment_id UUID REFERENCES experiments(experiment_id)
);

CREATE TABLE genotypes (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR,
    probe VARCHAR,
    genotype TEXT,
    confidence FLOAT,
    call_method TEXT,
    experiment_id UUID REFERENCES experiments(experiment_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);