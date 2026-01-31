# NewYork-taxi-data

Production-ready ETL pipeline for NYC taxi data. Ingests, processes, and loads NYC taxi trip data into PostgreSQL using Docker, pgAdmin, and Python.

## Project Overview

This pipeline:
- **Downloads** NYC taxi data (CSV format) from GitHub releases
- **Transforms** data with proper typing and validation
- **Loads** into PostgreSQL database
- **Manages** via pgAdmin web interface

## Setup

### Prerequisites

- Docker & Docker Compose installed
- 2GB free disk space
- Ports 5432 (PostgreSQL) and 8085 (pgAdmin) available

### Quick Start

```bash
cd pipeline
docker-compose up -d
```

Verify services started:
```bash
docker-compose ps
```

## Accessing Your Database

### pgAdmin Web UI (Recommended)
- **URL**: http://localhost:8085
- **Login**: admin@admin.com / root

Steps:
1. Click **Servers** → **Register** → **Server**
2. Name: `ny_taxi` | Host: `postgres` | Port: `5432`
3. Username: `root` | Password: `root`
4. Click **Save** and query your data

### PostgreSQL CLI

```bash
docker-compose exec postgres psql -U root -d ny_taxi
```

Example queries:
```sql
\dt                                    -- List tables
SELECT COUNT(*) FROM yellow_taxi_trips_2021_1;
SELECT * FROM yellow_taxi_trips_2021_1 LIMIT 5;
SELECT AVG(fare_amount) FROM yellow_taxi_trips_2021_1;
```

## Load Data

### Load 2021 Yellow Taxi Data

```bash
docker run -it --rm \
  --network=pipeline_pg-network \
  taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=postgres \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_1 \
  --chunksize=100000
```

### Load Other Months

```bash
for month in {01..12}; do
  docker run -it --rm --network=pipeline_pg-network taxi_ingest:v001 \
    --pg-host=postgres --pg-user=root --pg-pass=root --pg-db=ny_taxi \
    --target-table=yellow_taxi_2021_${month} \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-${month}.csv.gz
done
```

## Data Schema

Loaded tables include:
- `VendorID`, `tpep_pickup_datetime`, `tpep_dropoff_datetime`
- `passenger_count`, `trip_distance`
- `RatecodeID`, `PULocationID`, `DOLocationID`
- `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `total_amount`
- `payment_type`, `congestion_surcharge`

## Architecture

```
Data Source (GitHub)
    ↓
taxi_ingest Container (Python + Pandas)
    ↓
PostgreSQL 18 Database
    ↓
pgAdmin 4 UI
```

### Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| PostgreSQL | postgres:18 | 5432 | Data storage |
| pgAdmin | dpage/pgadmin4 | 8085 | Query & manage |
| taxi_ingest | Custom | — | ETL container |

## Development

### Run Pipeline Manually

```bash
cd pipeline
python ingest_data.py --help     # See all options
```

### View Notebooks

```bash
cd pipeline
jupyter notebook Notebook.ipynb
```

### View Logs

```bash
docker-compose logs -f postgres    # PostgreSQL logs
docker-compose logs -f pgadmin     # pgAdmin logs
```

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker volume rm pipeline_ny_taxi_postgres_data
docker-compose up -d
```

### Can't connect to PostgreSQL
- Ensure services are running: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`
- Verify host is `postgres` (not `localhost`) in pgAdmin

### Data not loading
```bash
docker-compose logs taxi_ingest
```

## Dependencies

Python dependencies managed in `pyproject.toml` using UV:
- `pandas` — Data transformation
- `psycopg2` — PostgreSQL connection
- `sqlalchemy` — ORM and utilities

## Project Structure

```
pipeline/
├── docker-compose.yaml        # Service orchestration
├── Dockerfile.ingest          # ETL container
├── ingest_data.py             # Main ingestion script
├── pipeline.py                # Utilities
├── main.py                    # Entry point
├── Notebook.ipynb             # Exploratory analysis
├── pyproject.toml             # Dependencies
└── uv.lock                    # Lock file
test/
├── file1.txt
├── file2.txt
├── file3.txt
└── script.py
```

## Next Steps

- [ ] Load full-year dataset
- [ ] Create SQL views for analytics
- [ ] Add data quality checks
- [ ] Set up automated ingestion schedule
- [ ] Add unit tests
