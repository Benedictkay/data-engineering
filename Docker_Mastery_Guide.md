# Docker Mastery Guide: Your Data Engineering Project Breakdown

## **Project Overview**

Your project ingests NYC taxi data into PostgreSQL and provides a UI (pgAdmin) to explore it. Three key services work together:

1. **PostgreSQL 18** - Database
2. **pgAdmin** - Web UI to query the database
3. **taxi_ingest** - Docker container that downloads and imports CSV data

---

## **Step-by-Step Breakdown**

### **Step 1: Understanding Docker Networking (The Foundation)**

**The Problem You Had:**
- Containers couldn't find each other by name
- `failed to resolve host 'postgres'` error

**The Solution:**
```
docker network create pipeline_pg-network
```

**Key Principle:**
- Containers are isolated by default (like separate computers)
- A network is like plugging cables between them
- Once connected, they can reference each other by name via DNS

**Pro Tip:**
Always think: "Do these containers need to talk to each other?" → If yes, put them on the **same network**.

---

### **Step 2: Volume Mounting (Persistent Data)**

**The Problem:**
- Container stops → data deleted
- PostgreSQL data lost after restart

**The Solution:**
```
volumes:
  - ny_taxi_postgres_data:/var/lib/postgresql
```

**What's Happening:**
- `-v` or `volumes:` creates a mapping
- Host storage (`ny_taxi_postgres_data`) ↔ Container storage (`/var/lib/postgresql`)
- Data persists even if container is deleted

**Gotcha Moment (You Experienced This!):**
```
WRONG for postgres:18
-v ny_taxi_postgres_data:/var/lib/postgresql/data

CORRECT for postgres:18
-v ny_taxi_postgres_data:/var/lib/postgresql
```

The difference: Postgres 18+ changed where it stores data. Always check the image documentation!

**Hack:** Create a `.env` file to manage versions:
```
POSTGRES_VERSION=18
POSTGRES_DATA_PATH=/var/lib/postgresql
```

---

### **Step 3: Environment Variables (Container Configuration)**

**The Problem:**
- Hardcoding passwords and configs in code is bad
- Need to change settings without rebuilding images

**The Solution:**
```
environment:
  POSTGRES_USER: root
  POSTGRES_PASSWORD: root
  POSTGRES_DB: ny_taxi
```

**Why It Matters:**
- Different environments (dev, staging, prod) need different configs
- Secrets stay out of version control
- Easy to swap configurations

**Pro Trick - Use `.env` file:**
```
.env
POSTGRES_USER=root
POSTGRES_PASSWORD=root
POSTGRES_DB=ny_taxi
```

```
docker-compose.yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

---

### **Step 4: Port Mapping (Accessing Services)**

**The Problem:**
- PostgreSQL runs inside container on port 5432
- But your machine also uses port 5432
- How do you access it?

**The Solution:**
```
ports:
  - "5432:5432"
```

Translation: `HOST_PORT:CONTAINER_PORT`

```
-p 5432:5432    # Access container's 5432 from host's 5432
-p 9000:5432    # Access container's 5432 from host's 9000
```

**When to Use Port Mapping:**
- External access (pgAdmin UI, local tools)
- **Don't map ports for internal container communication** (use network instead)

---

### **Step 5: Docker Compose (The Game Changer)**

**The Problem:**
```
Manual approach - error-prone, hard to remember
docker network create pg-network
docker run -d --name postgres --network pg-network -e POSTGRES_USER=root ... postgres:18
docker run -d --name pgadmin --network pg-network ... dpage/pgadmin4
What if you forget a parameter? Containers crash silently
```

**The Solution:**
One `docker-compose.yaml` file defines everything:
```
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: root
    volumes:
      - data:/var/lib/postgresql
    networks:
      - pg-network
    
  pgadmin:
    image: dpage/pgadmin4
    depends_on:
      - postgres
    networks:
      - pg-network

networks:
  pg-network:
```

**One command to rule them all:**
```
docker-compose up -d      # Start all services
docker-compose down       # Stop all services
docker-compose logs       # View all logs
docker-compose ps         # See all containers
```

---

## **The Most Important Concepts That NEVER Change**

### **1. Service Names vs Container Names**

**With docker run:**
```
docker run --name my-postgres postgres:18
Access via: my-postgres (the container name)
```

**With docker-compose:**
```
services:
  postgres:    # ← This is the SERVICE name
    container_name: my-postgres
```
- Access via: `postgres` (service name) - recommended
- NOT `my-postgres` (container name)

**Rule:** In docker-compose, use **service names** for inter-container communication.

---

### **2. The Network Requirement**

Every time containers need to talk:
```
docker run --network=my-network ...
```

**Without it:** "Name does not resolve" error (you got this one!)

---

### **3. Health Checks**

**Pro Trick - Wait for dependencies:**
```
postgres:
  image: postgres:18
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U root"]
    interval: 10s
    timeout: 5s
    retries: 5

pgadmin:
  depends_on:
    postgres:
      condition: service_healthy  # Wait until postgres is healthy
```

Without this, pgAdmin might start before postgres is ready.

---

## **Hacks to Master Docker**

### **Hack #1: Debug Container Issues**
```
# See what went wrong
docker logs container-name

# Inspect container configuration
docker inspect container-name

# Run a command inside a running container
docker exec -it container-name bash
```

### **Hack #2: Clean Up Everything**
```
# Remove all stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove all unused images
docker image prune -a

# Nuclear option: reset Docker
docker system prune -a --volumes
```

### **Hack #3: Quick Testing**
```
# Spin up a temporary database to test
docker run --rm -d --name test-db \
  -e POSTGRES_PASSWORD=test \
  -p 5433:5432 \
  postgres:18

# Test connection
psql -h localhost -p 5433 -U postgres

# Auto-cleanup when stopped
docker stop test-db
```

### **Hack #4: Environment-Specific Compose Files**
```
# docker-compose.yaml (base)
# docker-compose.prod.yaml (production overrides)

docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up
```

### **Hack #5: Watch Logs in Real-Time**
```
# Follow logs from all services
docker-compose logs -f

# Follow specific service
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100
```

---

## **The Workflow to Never Get Confused**

### **Step 1: Define Your Services (docker-compose.yaml)**
Ask yourself:
- What services do I need?
- What environment variables?
- What volumes for persistence?
- What ports for external access?

### **Step 2: Network Them**
```
networks:
  my-network:
    driver: bridge
```
Add `networks: [my-network]` to each service.

### **Step 3: Set Dependencies**
```
depends_on:
  - postgres
```
Ensures startup order.

### **Step 4: Test Locally**
```
docker-compose up -d
docker-compose ps
docker-compose logs
```

### **Step 5: Verify Connectivity**
```
# Test from one container to another
docker exec pgadmin ping postgres

# If it works, your networking is correct!
```

---

## **Common Pitfalls & Solutions**

| Problem | Cause | Solution |
|---------|-------|----------|
| Name does not resolve | Containers not on same network | Add networks: to docker-compose |
| Connection refused | Port not mapped | Add ports: ["HOST:CONTAINER"] |
| Data lost after restart | No volume mount | Add volumes: with persistent path |
| Postgres won't start | Wrong data path | Check :/var/lib/postgresql (not /data) |
| pgAdmin can't find postgres | Using container name instead of service name | Use service name: postgres not pg-database |

---

## **Your Project: The Complete Picture**

```
docker-compose up -d
    ↓
Creates network: pipeline_pg-network
    ↓
Starts: postgres (port 5432, data volume)
    ↓
Starts: pgadmin (port 8085, connects to postgres)
    ↓
You run: docker run ... --network=pipeline_pg-network taxi_ingest:v001
    ↓
taxi_ingest connects to "postgres" (service name on same network)
    ↓
Data flows: CSV → Pandas → PostgreSQL → pgAdmin UI
```

---

## **Master-Level Tricks**

1. **Use `.dockerignore`** - Don't copy unnecessary files
2. **Layer caching** - Order Dockerfile commands for faster rebuilds
3. **Health checks** - Know when services are actually ready
4. **Resource limits** - Prevent one container from crashing others
   ```
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```
5. **Logging drivers** - Send logs to external systems (ELK, Splunk)

---

## **Bottom Line**

Master these principles and you'll never be confused:

1. **Networks** = containers talking
2. **Volumes** = persistent data
3. **Environment variables** = configuration
4. **docker-compose** = reproducibility
5. **Service names** = the glue binding everything

Now you've got the keys to the kingdom!

---

## **Quick Reference Cheat Sheet**

### Essential Commands
```
docker-compose up -d              Start services in background
docker-compose down               Stop and remove services
docker-compose logs -f            Follow logs
docker-compose ps                 List running services
docker-compose exec postgres bash Connect to postgres container
docker ps                          List all running containers
docker logs container-name         View container logs
docker inspect container-name      Get container details
docker exec -it container bash     Open shell in container
docker network ls                  List networks
docker volume ls                   List volumes
docker system prune -a --volumes   Clean everything
```

### Common docker-compose.yaml Template
```
version: '3.8'

services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    volumes:
      - postgres_data:/var/lib/postgresql
    ports:
      - "5432:5432"
    networks:
      - main-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U root"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: root
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    ports:
      - "8085:80"
    networks:
      - main-network
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
  pgadmin_data:

networks:
  main-network:
    driver: bridge
```

---

**Document Version:** 1.0
**Created:** January 27, 2026
**Author:** GitHub Copilot
