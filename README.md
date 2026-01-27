# NYC Taxi Data Engineering Pipeline

A production-ready data engineering pipeline that ingests, processes, and manages NYC taxi trip data using Docker, PostgreSQL, and pgAdmin. This project demonstrates best practices in containerization, data orchestration, and database management.

## 📋 Project Overview

This project creates a scalable ETL (Extract, Transform, Load) pipeline that:

- **Extracts** NYC taxi trip data from GitHub releases (CSV format)
- **Transforms** data with proper data typing and validation
- **Loads** processed data into PostgreSQL 18 database
- **Manages** database through pgAdmin web interface
- **Orchestrates** all services using Docker Compose

### Architecture

```
Data Source (CSV)
       ↓
   taxi_ingest Container
   (Download & Transform)
       ↓
PostgreSQL 18 Database
       ↓
   pgAdmin 4 UI
   (Query & Manage)
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- 2GB free disk space minimum
- Port 5432 and 8085 available

### Launch Services

```bash
cd pipeline
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

Expected output:
```
NAME                     IMAGE              STATUS
pipeline-postgres-1      postgres:18        Up X seconds
pgadmin                  dpage/pgadmin4     Up X seconds
```

### Access Services

- **pgAdmin Web UI**: http://localhost:8085
  - Email: `admin@admin.com`
  - Password: `root`
  - Connect to: `postgres` (service name) on port 5432

- **PostgreSQL Direct**:
  - Host: `localhost`
  - Port: `5432`
  - Username: `root`
  - Password: `root`
  - Database: `ny_taxi`

---

## 📊 Loading Data

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

### Load Custom Dataset

```bash
docker run -it --rm \
  --network=pipeline_pg-network \
  taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=postgres \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=your_table_name \
  --chunksize=100000 \
  --url=https://path/to/your/data.csv.gz
```

### Data Schema

Loaded data includes:
- VendorID, Pickup & Dropoff DateTime
- Passenger Count, Trip Distance
- Rate Code, Location IDs
- Fare Details (base, tip, tax, surcharge)
- Payment Type, Congestion Surcharge

---

## 📁 Project Structure

```
data-engineering/
├── README.md                          # This file
├── Docker_Mastery_Guide.md           # Comprehensive Docker documentation
│
└── pipeline/
    ├── docker-compose.yaml           # Services orchestration
    ├── Dockerfile                    # PostgreSQL setup (if custom)
    ├── Dockerfile.ingest             # Data ingest container
    ├── ingest_data.py                # Python ingest script
    ├── main.py                       # Main pipeline orchestrator
    ├── pipeline.py                   # Pipeline utilities
    ├── pyproject.toml                # Python dependencies (UV)
    ├── README.md                     # Pipeline-specific docs
    └── Notebook.ipynb                # Exploratory data analysis
```

---

## 🔧 Services Configuration

### PostgreSQL 18
- **Image**: `postgres:18`
- **Port**: 5432 (host) → 5432 (container)
- **Data Persistence**: Volume `pipeline_ny_taxi_postgres_data`
- **Credentials**: root/root
- **Database**: ny_taxi

### pgAdmin 4
- **Image**: `dpage/pgadmin4`
- **Port**: 8085 (host) → 80 (container)
- **Credentials**: admin@admin.com / root
- **Data Persistence**: Volume `pipeline_pgadmin_data`

### taxi_ingest Container
- **Purpose**: CSV download and data ingestion
- **Network**: Connects to `pipeline_pg-network`
- **Configurable Parameters**: All via CLI arguments

### Docker Network
- **Name**: `pipeline_pg-network`
- **Type**: Bridge
- **Purpose**: Inter-container communication

---

## 🛠️ Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 postgres
```

### Connect to PostgreSQL

```bash
# Via docker-compose
docker-compose exec postgres psql -U root -d ny_taxi

# Sample queries
SELECT COUNT(*) FROM yellow_taxi_trips_2021_1;
SELECT AVG(fare_amount) FROM yellow_taxi_trips_2021_1;
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart postgres

# Full restart
docker-compose down
docker-compose up -d
```

### Clean Up

```bash
# Stop services (keep volumes)
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Full cleanup
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### "Name does not resolve" Error

**Cause**: Container not on same network or wrong hostname used

**Solution**:
```bash
# Ensure network in command
--network=pipeline_pg-network

# Use service name (not container name)
--pg-host=postgres
```

### PostgreSQL Won't Start

**Cause**: Incompatible data directory (likely from postgres:13)

**Solution**:
```bash
# Remove old volume and restart
docker-compose down
docker volume rm pipeline_ny_taxi_postgres_data
docker-compose up -d
```

### Connection Refused

**Cause**: Services not fully started

**Solution**:
```bash
# Wait a few seconds and check
sleep 3
docker-compose ps

# View startup logs
docker-compose logs postgres
```

### pgAdmin Can't Find Database

**Cause**: Using wrong hostname in pgAdmin connection settings

**Solution**:
- Host: `postgres` (service name)
- Port: `5432`
- Username: `root`
- Password: `root`

---

## 📈 Scaling & Best Practices

### Load Multiple Months

Create a script `load_multiple_months.sh`:
```bash
#!/bin/bash
for month in {01..12}; do
  docker run -it --rm --network=pipeline_pg-network taxi_ingest:v001 \
    --pg-host=postgres --pg-user=root --pg-pass=root --pg-db=ny_taxi \
    --target-table=yellow_taxi_2021_${month} \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-${month}.csv.gz
done
```

### Environment Management

Use `.env` file for configuration:
```bash
# .env
POSTGRES_USER=root
POSTGRES_PASSWORD=root
POSTGRES_DB=ny_taxi
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=root
```

Then in `docker-compose.yaml`:
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### Resource Limits

Add to `docker-compose.yaml`:
```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 📚 Key Concepts

### Docker Networking
- Containers are isolated by default
- Networks enable inter-container communication
- Service names (not container names) used for DNS resolution

### Volume Mounting
- Persistent data stored in volumes
- Data survives container restarts
- PostgreSQL 18 uses `/var/lib/postgresql` (not `/data`)

### Environment Variables
- Container configuration without rebuilding images
- Different configs for dev/staging/prod
- Secrets kept out of version control

### Docker Compose
- Single file defines all services
- `docker-compose up -d` starts everything
- One source of truth for infrastructure

---

## 🔐 Security Notes

⚠️ **For Development Only**

Current configuration is suitable for local development:
- Default credentials (root/root)
- No SSL/TLS
- All services exposed locally

**For Production**:
- Use strong passwords
- Enable SSL/TLS
- Use Docker secrets or external secret managers
- Implement authentication & authorization
- Set resource limits
- Enable logging & monitoring
- Use private networks

---

## 📖 Documentation

Comprehensive Docker and architecture documentation available in:
- [`Docker_Mastery_Guide.md`](Docker_Mastery_Guide.md) - Complete Docker reference with tricks and best practices

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Open a pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker logs: `docker-compose logs -f`
3. Consult `Docker_Mastery_Guide.md` for detailed explanations

---

## 🎯 Project Status

✅ Initial Setup Complete
✅ Docker Compose Configuration
✅ Data Ingestion Pipeline
✅ pgAdmin Integration
✅ Documentation

**Next Steps** (Future Enhancements):
- [ ] Airflow orchestration
- [ ] Data quality checks
- [ ] Advanced analytics queries
- [ ] Performance optimization
- [ ] CI/CD integration
- [ ] Automated testing

---

**Last Updated**: January 27, 2026
**Version**: 1.0.0
**Status**: Production Ready
