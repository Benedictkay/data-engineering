# data-engineering

This workspace is a monorepo that holds multiple data engineering projects and assignments. The root README documents the workspace layout and how the repository is intended to be organized; each project contains its own README with project-specific instructions (how to run, dependencies, and design).

Workspace layout

```
data-engineering/
├── NewYork-taxi-data/    # Project: ETL pipeline for NYC taxi data (see its README)
├── homework/             # Assignments and exercises (each assignment should have a folder and README)
└── README.md             # This file: workspace structure and intent
```

How to add a new project

- Create a new folder at the repository root (e.g. `my-new-project/`).
- Add a `README.md` inside that folder describing how to build, run, and test the project.
- Keep project dependencies and configs inside the project folder (e.g. `pyproject.toml`, `docker-compose.yaml`).
- If multiple projects share code, add a top-level `shared/` folder and reference it explicitly.

Guidelines

- Root README: only explains workspace structure and conventions.
- Project README: documents project purpose, setup, run instructions, and dependencies.
- Keep CI, docs, and shared utilities at the top-level when they are truly shared across projects.

That's it — open a project folder (for example, `NewYork-taxi-data/`) to find project-specific documentation and instructions.
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
