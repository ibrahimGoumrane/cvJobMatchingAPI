# Backend Startup Guide

This guide describes how to set up and run the AI Recruiter Backend API.

## Prerequisites
- **Python 3.10+** installed.
- **MySQL** database running locally or accessible via network.
- **Ollama** running locally with the following models pulled:
  - `llama3:latest`
  - `snowflake-arctic-embed2:latest`

## 1. Environment Setup

1. Navigate to the project root: `learning-app-backend`.
2. Ensure you have the `api/.env` file configured with your database credentials:
   ```env
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=ai_recruiter
   UPLOAD_FOLDER=uploads/
   ```

## 2. Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   .\env\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r api/requirements.txt
   ```
   *Note: This requirements file includes dependencies for both the API (`fastapi`, `uvicorn`) and the pipeline logic (`langchain`, `pypdfium2`, etc.).*

## 3. Running the Server

Start the FastAPI server using `uvicorn`. Run this command from the **root directory** (`learning-app-backend`):

```bash
uvicorn api.main:app --reload
```

- The server will start at `http://localhost:8000`.
- API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## 4. Verification

1. Check if the database tables are created automatically on startup.
2. Visit `http://localhost:8000/docs` to see the endpoints.
