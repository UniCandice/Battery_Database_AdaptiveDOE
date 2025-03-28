import pandas as pd
from sqlalchemy import create_engine

# 1. Establish connection
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/Battery_1')

# 2. Run queries and print results with clear formatting
try:
    print("=== BASIC TABLE SUMMARY ===")
    full_table = pd.read_sql("SELECT * FROM Adaptive_DoE LIMIT 5", engine)
    print(full_table.to_string(index=False))  # to_string() for cleaner output
    print("\nShape:", full_table.shape)
    
    print("\n=== FILTERED RESULTS (Resistance < 50) ===")
    filtered = pd.read_sql("""
        SELECT formulation_name, lfp_content, resistance_016_mpa 
        FROM Adaptive_DoE 
        WHERE resistance_016_mpa < 50
        ORDER BY resistance_016_mpa ASC
    """, engine)
    print(filtered.to_markdown(index=False, tablefmt="grid"))  # Fancy grid format
    print("\nFound", len(filtered), "matching formulations")
    
    print("\n=== STATISTICAL SUMMARY ===")
    stats = pd.read_sql("""
        SELECT 
            AVG(resistance_016_mpa)::numeric(10,2) as avg_resistance,
            MIN(resistance_016_mpa)::numeric(10,2) as min_resistance,
            MAX(resistance_016_mpa)::numeric(10,2) as max_resistance,
            COUNT(*) as total_samples
        FROM Adaptive_DoE
    """, engine)
    print(stats.transpose().to_string(header=False))  # Vertical display
    
    print("\n=== GROUP BY LFP TYPE ===")
    grouped = pd.read_sql("""
        SELECT 
            lfp_type,
            COUNT(*) as count,
            AVG(adhesion_force)::numeric(10,2) as avg_adhesion,
            AVG(viscosity_10s1)::numeric(10,2) as avg_viscosity
        FROM Adaptive_DoE
        GROUP BY lfp_type
    """, engine)
    print(grouped.to_string(index=False))

finally:
    engine.dispose()