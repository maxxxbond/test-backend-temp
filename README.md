# LingvalexaEducation API

FastAPI backend for the LingvalexaEducation platform, using Supabase for database and BunnyCDN for video streaming.

## Features

- User authentication and authorization
- Course management
- Video uploading and streaming with BunnyCDN
- Fully typed with Pydantic models
- Supabase integration for database operations

## Tech Stack

- Python 3.11+
- FastAPI
- Supabase
- BunnyCDN
- Docker & Docker Compose

## Setup & Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for local development with Supabase)

### Environment Setup

1. Clone the repository
2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the provided `.env.example`:

```bash
# Copy the example env file and modify it with your own values
cp .env.example .env
```

Edit the `.env` file with your specific configuration values, especially:

- Your Supabase URL and key
- Your BunnyCDN API key and zone names
- A secure secret key for JWT token signing

### Running the Application

#### With Python directly

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python run.py
```

The API will be available at http://localhost:8000

#### With Docker Compose

```bash
docker-compose up -d
```

This will start both the FastAPI application and a local Supabase instance.

- FastAPI API: http://localhost:8000
- Supabase Studio: http://localhost:54322

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Directory Structure

```
.
├── app/
│   ├── api/
│   │   ├── endpoints/       # API route handlers
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── courses.py   # Course management endpoints
│   │   │   ├── users.py     # User management endpoints
│   │   │   └── videos.py    # Video management endpoints
│   │   ├── api.py           # API router configuration
│   │   └── deps.py          # Dependency injection
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   └── security.py      # Security utilities
│   ├── db/
│   │   └── database.py      # Database utilities
│   ├── schemas/
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── bunnycdn.py      # BunnyCDN service
│   │   └── users.py         # User service
│   └── main.py              # Application entrypoint
├── supabase/
│   └── init.sql             # Database initialization SQL
├── tests/                   # Test suite
├── .env                     # Environment variables
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── run.py                   # Script to run the application
```
