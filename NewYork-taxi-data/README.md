# NewYork-taxi-data

ETL pipeline for NYC taxi data. Ingests, processes, and loads NYC taxi trip data into PostgreSQL using Docker and pgAdmin.

## Setup

### Prerequisites

- Docker & Docker Compose installed
- 2GB free disk space

### Quick Start

```bash
cd pipeline
docker-compose up -d
```

Services:
- **pgAdmin**: http://localhost:8085 (admin@admin.com / root)
- **PostgreSQL**: localhost:5432 (root / root)

## Load Data

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

## Dependencies

Python dependencies in `pyproject.toml` (managed with UV).

## Structure

- `pipeline/` - Docker compose, ingest scripts, and Jupyter notebook
- `test/` - Test files
