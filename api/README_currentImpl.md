# Backend API Implementation Status

## Overview
This directory contains the FastAPI-based backend for the **AI Recruiter** application. It serves as the interface between the frontend and the core logic (CV matching pipeline).

## Project Structure
The `api` folder is organized as follows:

```
api/
├── config/         # Configuration settings (To be implemented)
├── controller/     # API Route handlers (Endpoints)
├── entity/         # Database models (SQLAlchemy)
├── service/        # Business logic and coordination
├── socket/         # WebSocket handlers for real-time updates
├── utils/          # Utility functions
└── main.py         # Application entry point
```

## key Modules & Current Implementation

### 1. Entry Point (`main.py`)
- Initializes the `FastAPI` application.
- Registers routers:
  - `job_controller` under `/api/v1` prefix.
  - `job_socket` for WebSocket connections.

### 2. Controllers (`controller/`)
- **`job_controller.py`**:
  - `POST /api/v1/jobs`
    - **Purpose**: Accepts file uploads (CV and Job Description).
    - **Current State**: Stub implementation. Returns a mock `job_id` and status `PROCESSING`. Should eventually trigger the background processing pipeline.

### 3. WebSockets (`socket/`)
- **`job_socket.py`**:
  - `ws /ws/jobs/{job_id}`
    - **Purpose**: Provides real-time progress updates to the client for a specific job.
    - **Current State**: Accepts connections and sends an initial `STARTED` message.

### 4. Services (`service/`)
- **`job_service.py`**:
  - **Purpose**: Intended to bridge the API and the `cvJobMatching` pipeline.
  - **Current State**: Contains a scaffold function `run_evaluation` awaiting integration with the core pipeline logic.

### 5. Entities (`entity/`)
- **`base.py`**: 
  - **Purpose**: Base configuration for SQLAlchemy ORM models.
  - **Current State**: `DeclarativeBase` setup.

## Next Steps
- Implement actual file saving logic in `job_controller`.
- Integrate `cvJobMatching` pipeline calls in `job_service`.
- Flesh out `job_service` to process files and push updates to the WebSocket.
- Define database models in `entity` to persist job and evaluation results.
