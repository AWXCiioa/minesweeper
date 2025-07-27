# 🚀 Minesweeper Setup Guide

This guide provides detailed setup instructions for the Advanced Minesweeper web application, including development environment setup, deployment options, and troubleshooting.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Development Setup](#development-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing Setup](#testing-setup)
- [Production Deployment](#production-deployment)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)

## 🖥️ System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 512 MB available
- **Storage**: 100 MB free space
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 2 GB available
- **Storage**: 1 GB free space
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Development Tools (Optional)
- **IDE**: VS Code, PyCharm, or similar
- **Git**: For version control
- **Docker**: For containerized deployment
- **Postman**: For API testing

## 🛠️ Development Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd minesweeper

# Verify project structure
ls -la
```

Expected structure:
```
minesweeper/
├── public/
├── server/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── SETUP_GUIDE.md
```

### Step 2: Python Environment Setup

#### Option A: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

#### Option B: Using Conda

```bash
# Create conda environment
conda create -n minesweeper python=3.9
conda activate minesweeper
```

### Step 3: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-asyncio pytest-cov httpx black flake8 mypy
```

### Step 4: Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify FastAPI installation
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
```

## ⚙️ Environment Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit the file with your preferred settings
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

### Step 2: Configuration Options

```bash
# Database Configuration
DATABASE_URL=sqlite:///./minesweeper.db

# Server Configuration
HOST=0.0.0.0                    # Listen on all interfaces
PORT=8000                       # Default port
DEBUG=True                      # Enable debug mode for development

# CORS Configuration (adjust for your frontend URL)
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]

# Logging Configuration
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Game Configuration
MAX_LEADERBOARD_ENTRIES=100     # Maximum entries in leaderboard
```

### Step 3: Production Configuration

For production deployment, update these settings:

```bash
# Production settings
DEBUG=False
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000

# Update CORS origins to your domain
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Use PostgreSQL for production (optional)
DATABASE_URL=postgresql://user:password@localhost/minesweeper
```

## 🗄️ Database Setup

### SQLite Setup (Default)

SQLite requires no additional setup. The database file will be created automatically when you first run the application.

```bash
# Database will be created at: ./minesweeper.db
# No additional setup required
```

### PostgreSQL Setup (Production)

If using PostgreSQL for production:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Create database
createdb minesweeper

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/minesweeper
```

### Database Migration

The application automatically creates tables on startup. To manually initialize:

```python
# Run this Python script to initialize database
from server.db.sqlite_database import DatabaseManager

db = DatabaseManager()
print("Database initialized successfully!")
```

## 🚀 Running the Application

### Development Mode

```bash
# Method 1: Using Python module
python -m server.main

# Method 2: Direct execution
cd server
python main.py

# Method 3: Using uvicorn directly
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Application is Running

1. **Check console output:**
   ```
   INFO:     Started server process [12345]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Test endpoints:**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # API documentation
   curl http://localhost:8000/docs
   
   # Frontend
   curl http://localhost:8000/
   ```

3. **Open in browser:**
   - Game: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🧪 Testing Setup

### Install Test Dependencies

```bash
# Install testing packages
pip install pytest pytest-asyncio pytest-cov httpx

# Verify installation
pytest --version
```

### Run Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py unit
python tests/run_tests.py integration

# Run with coverage
pytest tests/ --cov=server --cov-report=html

# Run specific test
pytest tests/test_minesweeper.py::TestDatabaseManager::test_score_calculation -v
```

### Test Configuration

Create `pytest.ini` for custom test configuration:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## 🌐 Production Deployment

### Option 1: Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn server.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With configuration file
gunicorn -c gunicorn.conf.py server.main:app
```

Create `gunicorn.conf.py`:

```python
# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### Option 2: Using systemd (Linux)

Create `/etc/systemd/system/minesweeper.service`:

```ini
[Unit]
Description=Minesweeper Web Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/minesweeper
Environment=PATH=/path/to/minesweeper/venv/bin
ExecStart=/path/to/minesweeper/venv/bin/gunicorn server.main:app -c gunicorn.conf.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable minesweeper
sudo systemctl start minesweeper
sudo systemctl status minesweeper
```

### Option 3: Using Nginx Reverse Proxy

Install and configure Nginx:

```nginx
# /etc/nginx/sites-available/minesweeper
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (optional optimization)
    location /static/ {
        alias /path/to/minesweeper/public/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/minesweeper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🐳 Docker Setup

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "server.main"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  minesweeper:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///./data/minesweeper.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Add PostgreSQL
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: minesweeper
      POSTGRES_USER: minesweeper
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker build -t minesweeper .

# Run container
docker run -p 8000:8000 minesweeper

# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f minesweeper
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Error: Address already in use
# Solution: Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python -m server.main --port 8001
```

#### 2. Module Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'server'
# Solution: Run from project root directory
cd /path/to/minesweeper
python -m server.main

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/minesweeper"
```

#### 3. Database Permission Issues

```bash
# Error: Permission denied for database file
# Solution: Check file permissions
chmod 664 minesweeper.db
chown $USER:$USER minesweeper.db

# Or use different location
export DATABASE_URL="sqlite:///./data/minesweeper.db"
mkdir -p data
```

#### 4. CORS Issues

```bash
# Error: CORS policy blocks requests
# Solution: Update ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=["http://localhost:3000", "http://your-frontend-domain.com"]
```

#### 5. Static Files Not Loading

```bash
# Error: 404 for CSS/JS files
# Solution: Verify public directory structure
ls -la public/
# Should contain: index.html, style.css, script.js

# Check FastAPI static files mount
# In server/main.py, verify:
app.mount("/static", StaticFiles(directory="public"), name="static")
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Set in .env file
DEBUG=True
LOG_LEVEL=DEBUG

# Or set environment variable
export DEBUG=True
python -m server.main
```

### Logging Configuration

Configure detailed logging:

```python
# Add to server/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minesweeper.log'),
        logging.StreamHandler()
    ]
)
```

## ⚡ Performance Optimization

### Database Optimization

```python
# Add database indexes for better performance
# In server/db/sqlite_database.py, add:
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_games_player_difficulty 
    ON games(player_name, difficulty)
""")
```

### Caching

Add Redis caching for leaderboards:

```bash
# Install Redis dependencies
pip install redis

# Add to requirements.txt
redis==4.5.1
```

### Static File Optimization

```python
# Add compression and caching headers
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Production Optimizations

```bash
# Use production WSGI server
pip install gunicorn

# Optimize worker count (CPU cores * 2 + 1)
gunicorn server.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable keep-alive connections
gunicorn server.main:app --keep-alive 2

# Set appropriate timeouts
gunicorn server.main:app --timeout 30 --graceful-timeout 30
```

## 📊 Monitoring

### Health Checks

The application includes built-in health checks:

```bash
# Check application health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Metrics Collection

Add Prometheus metrics (optional):

```bash
pip install prometheus-fastapi-instrumentator

# Add to server/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Log Monitoring

Configure log rotation:

```python
# Add to logging configuration
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'minesweeper.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## 🔒 Security Considerations

### Production Security

1. **Disable Debug Mode**
   ```bash
   DEBUG=False
   ```

2. **Use HTTPS**
   ```bash
   # Configure SSL certificate
   gunicorn server.main:app --certfile=cert.pem --keyfile=key.pem
   ```

3. **Set Secure Headers**
   ```python
   # Add security middleware
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   
   app.add_middleware(
       TrustedHostMiddleware, 
       allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
   )
   ```

4. **Database Security**
   ```bash
   # Use strong database passwords
   # Limit database user permissions
   # Enable database encryption if needed
   ```

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** for detailed error messages
2. **Review the test suite** for examples of correct usage
3. **Consult the API documentation** at `/docs`
4. **Search existing issues** in the project repository
5. **Create a new issue** with detailed reproduction steps

---

**Happy coding! 🚀**
