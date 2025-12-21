# AI Recruiter API Service

## Overview

This project serves as the **FastAPI access layer** for the AI Recruitment system. Its primary purpose is to expose the core evaluation logic (`cvJobMatching` module) via high-performance, asynchronous REST endpoints and WebSockets.

It is designed to handle long-running inference tasks without blocking, providing real-time feedback to clients and persisting results to a MySQL database.

---

## Architecture

This service is strictly an **API Interface**. It decouples the serving logic from the core AI processing.

*   **API Framework**: **FastAPI** (Async/Input Validation).
*   **Core Module**: Imports and orchestrates the distinct `cvJobMatching` package.
*   **Database**: **MySQL** with **SQLAlchemy (Async)** for robust data persistence.
*   **Real-time Communication**: Native **WebSockets** for streaming pipeline progress (e.g., "Scanning CV...", "Generating Report...").

---

## Key Features

### 1. Asynchronous Evaluation
Long-running AI tasks (PDF parsing, LLM inference) are executed asynchronously. The API accepts a request and immediately returns a Job ID, preventing timeouts.

### 2. WebSocket Streaming
Clients connect to a WebSocket endpoint using the Job ID to receive live updates on the evaluation stages, ensuring a responsive user experience.

### 3. Persistent Storage
All evaluation reports, decisions, and user metadata are stored in a MySQL database. This allows for:
*   Historical record keeping.
*   Auditing of AI decisions.
*   User-specific dashboards.

---

## Tech Stack

This service focuses on the **serving and persistence** layer:

*   **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
*   **Uvicorn**: lightning-fast ASGI server implementation.
*   **SQLAlchemy (AsyncIO)**: SQL toolkit and ORM for database interactions.
*   **aiomysql**: Asyncio driver for MySQL.
*   **Pydantic**: Data validation and settings management using python type hinting.
*   **WebSockets**: Standard library support within FastAPI.

---

## API Roadmap

*   `POST /api/v1/jobs` - Submit a new CV/Job pair for evaluation.
*   `WS /ws/jobs/{job_id}` - Stream status and results.
*   `GET /api/v1/jobs/{job_id}` - Retrieve past results (from MySQL).
*   `GET /api/v1/history` - List all past evaluations.

## Project Structure

The API service follows a modular architecture:

```
api/
├── config/         # App configuration & Database setups
├── controller/     # HTTP Enpoint handlers (Routes)
├── entity/         # Database Models (SQLAlchemy)
├── service/        # Business Logic & Core Integration
├── socket/         # WebSocket Managers & Handlers
├── utils/          # Shared utilities (Logging, Helpers)
├── main.py         # App Entrypoint
└── requirements.txt
```

---

## Running the API

```bash
# Install API dependencies (fastapi, database drivers, etc.)
pip install -r requirements.txt

# Start the server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
