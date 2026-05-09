# Supabase Configuration for VitaChain Backend

## Environment Variables

Create a `.env` file in the backend root directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:7-j9!Z%knXx5/s!@db.ymogoemuzqyjsdjhzpnz.supabase.co:5432/postgres
SUPABASE_URL=https://ymogoemuzqyjsdjhzpnz.supabase.co
SUPABASE_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ

# Application Configuration
APP_NAME=VitaChain Backend
VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Module Configuration
MODULE=katara

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=
```

## Supabase Client Setup

The backend should use the following configuration to connect to Supabase:

```python
from supabase import create_client, Client

supabase_url: str = "https://ymogoemuzqyjsdjhzpnz.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ"

supabase: Client = create_client(supabase_url, supabase_key)
```

## Database Connection

The application can connect directly to the PostgreSQL database using:

```python
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:7-j9!Z%knXx5/s!@db.ymogoemuzqyjsdjhzpnz.supabase.co:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

## Authentication

The backend should validate JWT tokens using the Supabase JWT secret:

```python
import jwt
from fastapi import HTTPException, Depends

def verify_supabase_token(token: str):
    try:
        payload = jwt.decode(
            token,
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ",
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```
