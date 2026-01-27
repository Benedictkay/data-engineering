# Pipeline Module - Data Ingestion Service

## Overview

This module contains the containerized data ingestion pipeline for the NYC Taxi Data Engineering project. It handles downloading, validating, and loading CSV data into PostgreSQL.

## Components

### `docker-compose.yaml`
Orchestrates three services:
- **postgres**: PostgreSQL 18 database
- **pgadmin**: Web-based database management UI
- **taxi_ingest**: Custom data ingestion container

### `ingest_data.py`
Core Python script that:
- Downloads CSV files (gzip-compressed)
- Validates and transforms data with proper data types
- Iteratively loads data in configurable chunks
- Handles database schema creation
- Provides progress tracking with tqdm

**Key Features**:
- Automated table creation
- Configurable chunk sizes (default: 100,000 rows)
- Proper data type mapping (Int64, float64, string, datetime)
- Connection pooling via SQLAlchemy
- Progress bar for long-running operations

### `Dockerfile.ingest`
Custom Docker image containing:
- Python environment with dependencies
- Data validation libraries
- PostgreSQL client tools
- Pre-configured entry point

### `pyproject.toml`
Python dependency management using UV:
- pandas: Data manipulation
- sqlalchemy: Database ORM
- psycopg2-binary: PostgreSQL adapter
- tqdm: Progress bars

## Usage

### Quick Start

```bash
# Start all services
docker-compose up -d

# Verify services running
docker-compose ps

# Load data
docker run -it --rm \
  --network=pipeline_pg-network \
  taxi_ingest:v001 \
  --pg-host=postgres \
  --pg-user=root \
  --pg-pass=root \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips_2021_1 \
  --chunksize=100000

# Stop services
docker-compose down
```

### Command Line Arguments

```bash
--pg-user         PostgreSQL username (required)
--pg-pass         PostgreSQL password (required)
--pg-host         PostgreSQL hostname/IP (required)
--pg-port         PostgreSQL port (default: 5432)
--pg-db           Database name (required)
--target-table    Destination table name (required)
--url             CSV file URL (default: 2021-01 yellow taxi)
--chunksize       Rows per batch (default: 100000)
```

### Examples

**Load 2021 Q1 Data**:
```bash
docker run -it --rm --network=pipeline_pg-network taxi_ingest:v001 \
  --pg-host=postgres --pg-user=root --pg-pass=root --pg-db=ny_taxi \
  --target-table=yellow_taxi_2021_01 \
  --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

**Load with Custom Chunk Size**:
```bash
docker run -it --rm --network=pipeline_pg-network taxi_ingest:v001 \
  --pg-host=postgres --pg-user=root --pg-pass=root --pg-db=ny_taxi \
  --target-table=my_table \
  --chunksize=50000 \
  --url=https://path/to/data.csv.gz
```

## Data Schema

The ingest process creates tables with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| VendorID | Int64 | Vendor identifier |
| tpep_pickup_datetime | datetime | Pickup timestamp |
| tpep_dropoff_datetime | datetime | Dropoff timestamp |
| passenger_count | Int64 | Number of passengers |
| trip_distance | float64 | Trip distance in miles |
| RatecodeID | Int64 | Rate code |
| store_and_fwd_flag | string | Store and forward flag |
| PULocationID | Int64 | Pickup location ID |
| DOLocationID | Int64 | Dropoff location ID |
| payment_type | Int64 | Payment method |
| fare_amount | float64 | Fare amount |
| extra | float64 | Extra charges |
| mta_tax | float64 | MTA tax |
| tip_amount | float64 | Tip amount |
| tolls_amount | float64 | Toll amount |
| improvement_surcharge | float64 | Improvement surcharge |
| total_amount | float64 | Total amount |
| congestion_surcharge | float64 | Congestion surcharge |

## Docker Compose Services

### PostgreSQL 18

```yaml
postgres:
  image: postgres:18
  container_name: pipeline-postgres-1
  volumes:
    - ny_taxi_postgres_data:/var/lib/postgresql
  ports:
    - "5432:5432"
  networks:
    - pg-network
```

**Access**:
- Host: localhost or postgres (internal)
- Port: 5432
- User: root
- Password: root

### pgAdmin 4

```yaml
pgadmin:
  image: dpage/pgadmin4
  ports:
    - "8085:80"
  networks:
    - pg-network
  depends_on:
    - postgres
```

**Access**:
- URL: http://localhost:8085
- Email: admin@admin.com
- Password: root

**Connection Settings**:
- Host: postgres
- Port: 5432
- Username: root
- Password: root

## Common Operations

### Check Data Quality

```bash
# Connect to database
docker-compose exec postgres psql -U root -d ny_taxi

# Count rows
SELECT COUNT(*) FROM yellow_taxi_trips_2021_1;

# Check date range
SELECT MIN(tpep_pickup_datetime), MAX(tpep_pickup_datetime) 
FROM yellow_taxi_trips_2021_1;

# View schema
\d yellow_taxi_trips_2021_1
```

### Monitor Ingestion

```bash
# View logs during ingest
docker logs -f <container-id>

# Monitor database size
docker-compose exec postgres psql -U root -d ny_taxi -c \
  "SELECT pg_size_pretty(pg_database_size('ny_taxi'));"
```

### Backup Data

```bash
# Export table to CSV
docker-compose exec postgres pg_dump -U root ny_taxi \
  -t yellow_taxi_trips_2021_1 --data-only > backup.sql

# Full database backup
docker-compose exec postgres pg_dump -U root ny_taxi > ny_taxi_backup.sql
```

## Troubleshooting

### Network Issues

**Error**: `failed to resolve host 'postgres'`

**Solution**: Ensure container is on correct network
```bash
docker run --network=pipeline_pg-network ...
```

### Connection Refused

**Error**: `Cannot connect to postgres`

**Solution**: Wait for PostgreSQL to start
```bash
sleep 5
docker run -it --rm --network=pipeline_pg-network taxi_ingest:v001 ...
```

### Database Corruption

**Error**: PostgreSQL fails to start after version change

**Solution**: Clear volume and restart
```bash
docker-compose down
docker volume rm pipeline_ny_taxi_postgres_data
docker-compose up -d
```

### Out of Disk Space

**Solution**: Check and clean up
```bash
docker system df
docker system prune -a --volumes
```

## Performance Tips

1. **Increase Chunk Size**: Use `--chunksize=500000` for faster ingestion on powerful machines
2. **Parallel Loads**: Load multiple tables simultaneously (different containers)
3. **Index Creation**: Add indexes after loading for query optimization
4. **Connection Pooling**: SQLAlchemy handles this automatically

## Files Reference

| File | Purpose |
|------|---------|
| `docker-compose.yaml` | Service orchestration |
| `Dockerfile.ingest` | Custom image for ingest |
| `ingest_data.py` | Core ingestion logic |
| `main.py` | Pipeline orchestrator |
| `pipeline.py` | Utility functions |
| `pyproject.toml` | Python dependencies |
| `Notebook.ipynb` | Data exploration & analysis |

## Future Enhancements

- [ ] Incremental data loading (upsert)
- [ ] Data validation framework
- [ ] Automated scheduling (Airflow)
- [ ] Partitioned tables for large datasets
- [ ] CDC (Change Data Capture)
- [ ] Data quality metrics

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: January 27, 2026
