# 🚀 Deployment Guide

Deployment guide for Data Quality Checker API on various platforms.

## 📋 Table of Contents

- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Variables Configuration](#environment-variables-configuration)
- [Database Configuration](#database-configuration)
- [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Deployment

### Requirements

- Python 3.9, 3.10, or 3.11
- pip (Python package manager)

### Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd data-quality-checker
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env file as needed
   ```

5. **Run the application:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or use Makefile:
   ```bash
   make run
   ```

6. **Verify API is working:**
   - Open browser: http://localhost:8000/docs
   - Swagger UI will be available for API testing

---

## 🐳 Docker Deployment

### Quick Start

1. **Create `.env` file from example:**
   ```bash
   cp .env.example .env
   ```

2. **Build and run containers:**
   ```bash
   docker-compose up -d
   ```

3. **Check logs:**
   ```bash
   docker-compose logs -f api
   ```

4. **Open API documentation:**
   - http://localhost:8000/docs

### Docker Compose Commands

```bash
# Run in background
docker-compose up -d

# Stop
docker-compose down

# Rebuild and run
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Stop and remove volumes
docker-compose down -v
```

### Docker (without docker-compose)

1. **Build the image:**
   ```bash
   docker build -t data-quality-checker .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name data-quality-checker \
     -p 8000:8000 \
     -v $(pwd)/data/db/db.sqlite3:/app/data/db/db.sqlite3 \
     -v $(pwd)/reports:/app/reports \
     -v $(pwd)/tmp:/app/tmp \
     --env-file .env \
     data-quality-checker
   ```

---

## 🌐 Production Deployment

### Production Configuration

1. **Update `.env` file:**
   ```env
   ENVIRONMENT=production
   LOG_LEVEL=WARNING
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

2. **Use production-ready server:**
   ```bash
   # With gunicorn (recommended)
   pip install gunicorn
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Configure reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Configure SSL (Let's Encrypt):**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### Cloud Platform Deployment

#### Heroku

1. **Create `Procfile`:**
   ```
   web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set CORS_ORIGINS=https://yourdomain.com
   git push heroku main
   ```

#### AWS EC2 / DigitalOcean / Linode

1. **Connect to server via SSH**

2. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd data-quality-checker
   ```

4. **Run via Docker Compose:**
   ```bash
   docker-compose up -d
   ```

---

## ⚙️ Environment Variables Configuration

### Required Variables

- `CORS_ORIGINS` - Comma-separated list of allowed origins for CORS

### Optional Variables

- `DATABASE_URL` - Database URL (default: SQLite)
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT` - Environment (development/production)

See `.env.example` for the full list.

---

## 💾 Database Configuration

### SQLite (Default)

SQLite database is created automatically on first run. The `db.sqlite3` file will be created in the `data/db/` directory.

### PostgreSQL (Optional)

1. **Use PostgreSQL in docker-compose.yml:**
   - Uncomment the `postgres` section in `docker-compose.yml`

2. **Update DATABASE_URL:**
   ```env
   DATABASE_URL=postgresql://dataquality:changeme@postgres:5432/dataquality
   ```

3. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## 🔒 Security

### Production Recommendations

1. **Use HTTPS:**
   - Configure SSL/TLS certificate
   - Use Let's Encrypt for free certificates

2. **Limit CORS:**
   - Specify only necessary origins in `CORS_ORIGINS`
   - Don't use `*` in production

3. **Limit file size:**
   - Configure `MAX_FILE_SIZE` in `.env`
   - Configure reverse proxy to limit request size

4. **Use strong passwords:**
   - If using PostgreSQL, set a strong password

5. **Regularly update dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

---

## 🔧 Troubleshooting

### Issue: Port Already in Use

**Solution:**
```bash
# Find process on port 8000
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Database Not Created

**Solution:**
```bash
# Create database manually
python -c "from src.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Issue: Docker Container Not Starting

**Solution:**
```bash
# Check logs
docker-compose logs api

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Issue: CORS Errors

**Solution:**
- Ensure `CORS_ORIGINS` contains the correct origin
- Check that origin matches exactly (including protocol and port)

---

## 📞 Support

If you encounter deployment issues:

1. Check logs: `docker-compose logs -f api`
2. Check environment variables: `docker-compose config`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Last updated:** 2024

