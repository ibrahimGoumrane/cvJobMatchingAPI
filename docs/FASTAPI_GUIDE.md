# FastAPI Backend Architecture - Complete Guide

This document explains all the key concepts, patterns, and technologies used in building this AI Recruiter API. Use this as a reference for future FastAPI projects.

---

## Table of Contents
1. [FastAPI Basics](#fastapi-basics)
2. [Async/Await Pattern](#asyncawait-pattern)
3. [Database Integration with SQLAlchemy](#database-integration-with-sqlalchemy)
4. [WebSocket Communication](#websocket-communication)
5. [Background Tasks](#background-tasks)
6. [CORS Configuration](#cors-configuration)
7. [Error Handling](#error-handling)
8. [Logging System](#logging-system)
9. [Project Structure](#project-structure)
10. [Best Practices](#best-practices)

---

## FastAPI Basics

### What is FastAPI?
FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

### Key Features
- **Fast**: Very high performance, on par with NodeJS and Go
- **Type Safety**: Uses Python type hints for automatic validation
- **Auto Documentation**: Generates interactive API docs (Swagger UI)
- **Async Support**: Built-in support for async/await

### Basic Structure

```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Running the Server

```bash
uvicorn api.main:app --reload
```

- `api.main`: Module path (file `api/main.py`)
- `app`: FastAPI instance variable name
- `--reload`: Auto-reload on code changes (dev only)

---

## Async/Await Pattern

### Why Async?
Async programming allows handling multiple requests concurrently without blocking. Perfect for I/O-bound operations (database, file operations, API calls).

### Sync vs Async

**Synchronous (Blocking)**:
```python
def get_user(user_id: int):
    user = database.query(User).filter(User.id == user_id).first()  # Blocks here
    return user
```

**Asynchronous (Non-blocking)**:
```python
async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()  # Doesn't block other requests
        return user
```

### Key Concepts

1. **`async def`**: Defines an asynchronous function (coroutine)
2. **`await`**: Pauses execution until the awaited operation completes
3. **Event Loop**: Manages and executes async tasks

### When to Use Async

✅ **Use Async For**:
- Database queries
- File I/O operations
- HTTP requests to external APIs
- WebSocket connections

❌ **Don't Use Async For**:
- CPU-intensive computations (use `run_in_executor` instead)
- Simple synchronous operations

### Example: Running Sync Code in Async Context

```python
import asyncio

async def run_cpu_intensive_task():
    loop = asyncio.get_running_loop()
    
    # Run blocking code in thread pool
    result = await loop.run_in_executor(
        None,  # Use default executor
        lambda: heavy_computation()  # Your blocking function
    )
    return result
```

---

## Database Integration with SQLAlchemy

### SQLAlchemy ORM
Object-Relational Mapping (ORM) allows you to work with databases using Python objects instead of raw SQL.

### Async SQLAlchemy Setup

**1. Database Configuration** (`api/config/database.py`):

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async engine
engine = create_async_engine(
    "mysql+aiomysql://user:password@localhost/dbname",
    echo=True  # Log SQL queries
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**2. Define Models** (`api/entity/base.py`):

```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, DateTime

class Base(DeclarativeBase):
    pass

class JobProcessing(Base):
    __tablename__ = "job_processing"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
```

**3. Database Operations**:

```python
from sqlalchemy import select

async def create_job(job_data):
    async with AsyncSessionLocal() as session:
        new_job = JobProcessing(**job_data)
        session.add(new_job)
        await session.commit()
        return new_job

async def get_job(job_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(JobProcessing).where(JobProcessing.id == job_id)
        )
        return result.scalar_one_or_none()

async def get_all_jobs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(JobProcessing))
        return result.scalars().all()
```

### Application Lifecycle (Startup/Shutdown)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

---

## WebSocket Communication

### What are WebSockets?
WebSockets provide full-duplex communication channels over a single TCP connection. Unlike HTTP (request-response), WebSockets allow real-time, bidirectional communication.

### Use Cases
- Real-time progress updates
- Chat applications
- Live notifications
- Streaming data

### Implementation

**1. Connection Manager** (`api/socket/job_socket.py`):

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()
```

**2. WebSocket Endpoint**:

```python
@router.websocket("/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        # Send initial message
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "job_id": job_id
        })
        
        # Keep connection alive
        while True:
            await asyncio.sleep(60)
            
    except WebSocketDisconnect:
        manager.disconnect(job_id)
```

**3. Sending Updates from Background Tasks**:

```python
async def process_job(job_id: str):
    # Send progress update
    await manager.send_message(job_id, {
        "type": "PROGRESS",
        "progress": 50,
        "message": "Processing..."
    })
```

### Client-Side Connection (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Progress:', data.progress);
};

ws.onclose = () => {
    console.log('Connection closed');
};
```

---

## Background Tasks

### Why Background Tasks?
Long-running operations (file processing, ML inference) shouldn't block API responses. Background tasks allow immediate response while work continues.

### Two Approaches

**1. FastAPI Background Tasks** (Simple, same process):

```python
from fastapi import BackgroundTasks

async def send_email(email: str):
    # Simulate email sending
    await asyncio.sleep(5)
    print(f"Email sent to {email}")

@app.post("/register")
async def register(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Registration successful"}
```

**2. asyncio.create_task** (More control):

```python
async def long_running_task(job_id: str):
    # This runs in background
    await asyncio.sleep(10)
    print(f"Job {job_id} completed")

@app.post("/jobs")
async def create_job(job_id: str):
    # Create task and don't await it
    asyncio.create_task(long_running_task(job_id))
    return {"job_id": job_id, "status": "processing"}
```

### Running Sync Code in Background

```python
async def run_ml_model(job_id: str, data: dict):
    loop = asyncio.get_running_loop()
    
    # Run blocking ML inference in thread pool
    result = await loop.run_in_executor(
        None,
        lambda: ml_model.predict(data)
    )
    
    # Save result to database
    await save_result(job_id, result)
```

### Communicating with Main Thread

```python
async def background_worker(job_id: str):
    main_loop = asyncio.get_running_loop()
    
    def progress_callback(progress: int):
        # Schedule coroutine in main loop
        asyncio.run_coroutine_threadsafe(
            manager.send_message(job_id, {"progress": progress}),
            main_loop
        )
    
    # Pass callback to sync function
    await loop.run_in_executor(
        None,
        lambda: process_with_callback(progress_callback)
    )
```

---

## CORS Configuration

### What is CORS?
Cross-Origin Resource Sharing (CORS) allows your API to be accessed from different domains (e.g., frontend on `localhost:4200` accessing API on `localhost:8000`).

### Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # React dev server
    "https://yourdomain.com"  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (dev only!)
    allow_credentials=True,
    allow_methods=["*"],  # or ["GET", "POST"]
    allow_headers=["*"],
)
```

### Important Notes
- `allow_origins=["*"]` is convenient for development but **insecure for production**
- Always specify exact origins in production
- `allow_credentials=True` allows cookies/auth headers

---

## Error Handling

### Global Exception Handlers

```python
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation Error on {request.method} {request.url.path}")
    logger.error(f"Errors: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "message": "Validation Error",
            "data": {"detail": errors}
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "message": f"Internal Server Error: {str(exc)}"
        }
    )
```

### Custom Exceptions

```python
class JobNotFoundException(Exception):
    pass

@app.exception_handler(JobNotFoundException)
async def job_not_found_handler(request: Request, exc: JobNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": "Job not found"}
    )
```

---

## Logging System

### Setup Logging

```python
import logging
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

# Get logger in modules
logger = logging.getLogger(__name__)
```

### Using Loggers

```python
logger.debug("Detailed debug information")
logger.info("[JOB] Creating new job")
logger.warning("[WARN] Connection timeout, retrying...")
logger.error("[ERROR] Database connection failed", exc_info=True)
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (something unexpected)
- **ERROR**: Error messages (something failed)
- **CRITICAL**: Critical errors (system failure)

---

## Project Structure

```
learning-app-backend/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config/
│   │   ├── database.py         # Database configuration
│   │   └── logging_config.py   # Logging setup
│   ├── controller/
│   │   └── job_controller.py   # API endpoints (routes)
│   ├── service/
│   │   └── job_service.py      # Business logic
│   ├── entity/
│   │   └── base.py             # Database models
│   ├── schema/
│   │   └── job.py              # Pydantic models (validation)
│   ├── socket/
│   │   └── job_socket.py       # WebSocket handlers
│   └── utils/
│       └── ApiResponse.py      # Response models
├── cvJobMatching/              # ML pipeline module
├── logs/                       # Log files
├── uploads/                    # Uploaded files
├── docs/                       # Documentation
├── requirements.txt
└── .gitignore
```

### Layer Responsibilities

**Controller (Routes)**:
- Handle HTTP requests
- Validate input
- Call service layer
- Return responses

**Service (Business Logic)**:
- Implement business rules
- Coordinate between components
- Handle transactions

**Entity (Models)**:
- Define database schema
- ORM mappings

**Schema (Validation)**:
- Request/response validation
- Data serialization

---

## Best Practices

### 1. Type Hints
Always use type hints for better IDE support and automatic validation:

```python
async def create_user(name: str, age: int) -> User:
    pass
```

### 2. Dependency Injection
Use FastAPI's dependency system:

```python
from fastapi import Depends

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### 3. Pydantic Models
Use Pydantic for request/response validation:

```python
from pydantic import BaseModel

class JobCreate(BaseModel):
    user_id: str
    title: str

class JobResponse(BaseModel):
    id: str
    user_id: str
    status: str
    
    class Config:
        from_attributes = True  # For ORM models
```

### 4. Environment Variables
Never hardcode secrets:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 5. Error Handling
Always handle exceptions gracefully:

```python
try:
    result = await risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="Operation failed")
```

### 6. Testing
Write tests for your endpoints:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_job():
    response = client.post("/jobs", json={"user_id": "123"})
    assert response.status_code == 201
```

---

## Common Patterns

### 1. File Upload

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
    return {"filename": file.filename}
```

### 2. Form Data

```python
from fastapi import Form

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Authenticate
    return {"access_token": token}
```

### 3. Query Parameters

```python
@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return items[skip:skip+limit]
```

### 4. Path Parameters

```python
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}
```

---

## Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use specific CORS origins (not `*`)
- [ ] Enable HTTPS
- [ ] Use environment variables for secrets
- [ ] Set up proper logging
- [ ] Use a process manager (systemd, supervisor)
- [ ] Set up database migrations (Alembic)
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring
- [ ] Enable rate limiting

---

## Useful Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api.main:app --reload

# Run with specific host/port
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Run in production (with workers)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Generate requirements
pip freeze > requirements.txt

# Database migrations (Alembic)
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Python Async/Await**: https://docs.python.org/3/library/asyncio.html
- **Pydantic**: https://docs.pydantic.dev/
- **WebSockets**: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

## Summary

This API demonstrates:
- ✅ **FastAPI** for high-performance API development
- ✅ **Async/Await** for concurrent request handling
- ✅ **SQLAlchemy** for database operations
- ✅ **WebSockets** for real-time communication
- ✅ **Background Tasks** for long-running operations
- ✅ **Proper Error Handling** with global exception handlers
- ✅ **Comprehensive Logging** for debugging and monitoring
- ✅ **Clean Architecture** with separation of concerns

Use these patterns and concepts as a foundation for your future FastAPI projects!
