from sqlalchemy import create_engine

DATABASE_URL = "postgresql://genouser:password@localhost/genotype_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

