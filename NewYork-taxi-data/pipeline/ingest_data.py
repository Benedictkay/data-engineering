import argparse
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

def main():
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--pg-user', required=True, help='Postgres username')
    parser.add_argument('--pg-pass', required=True, help='Postgres password')
    parser.add_argument('--pg-host', required=True, help='Postgres host')
    parser.add_argument('--pg-port', default='5432', help='Postgres port')
    parser.add_argument('--pg-db', required=True, help='Postgres database name')
    parser.add_argument('--target-table', required=True, help='Target table name')
    parser.add_argument('--url', default='https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz', help='URL of the CSV file')
    parser.add_argument('--chunksize', type=int, default=100000, help='Chunk size for iteration')
    
    args = parser.parse_args()
    
    # Data types
    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64"
    }
    
    parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    
    # Create engine
    engine = create_engine(f'postgresql://{args.pg_user}:{args.pg_pass}@{args.pg_host}:{args.pg_port}/{args.pg_db}')
    
    # Create iterator
    df_iter = pd.read_csv(
        args.url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=args.chunksize
    )
    
    # Get first chunk and create table
    first_chunk = next(df_iter)
    first_chunk.head(n=0).to_sql(name=args.target_table, con=engine, if_exists='replace')
    print(f"Table {args.target_table} created")
    
    # Insert first chunk
    first_chunk.to_sql(name=args.target_table, con=engine, if_exists='append')
    print(f"Inserted first chunk: {len(first_chunk)} rows")
    
    # Insert remaining chunks
    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(name=args.target_table, con=engine, if_exists='append')
    
    print("Data ingestion complete!")

if __name__ == '__main__':
    main()
