# REST API Documentation

Base URL: `http://localhost:8000/api/v1`

## 1. Submit Job
Uploads a CV and Job Description to start the evaluation process.

- **Endpoint**: `POST /jobs`
- **Content-Type**: `multipart/form-data`

### Request Body
| Field | Type | Description |
|---|---|---|
| `user_id` | `integer` | ID of the user submitting the job |
| `cv` | `file` | The Resume/CV file (PDF, DOCX, TXT) |
| `jobdesc` | `file` | The Job Description file (PDF, DOCX, TXT) |

### Response (201 Created)
```json
{
  "status_code": 201,
  "message": "Job submitted successfully",
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "PROCESSING"
  }
}
```

---

## 2. Get All Jobs
Retrieves a list of all submitted jobs and their current status.

- **Endpoint**: `GET /jobs`

### Response (200 OK)
```json
{
  "status_code": 200,
  "message": "Jobs retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 1,
      "jobdesc_path": "uploads/550e84.../jd_job.pdf",
      "cv_path": "uploads/550e84.../cv_resume.pdf",
      "decision": "PASS",
      "report_path": "uploads/550e84.../evaluation_report.json",
      "progress": 100,
      "status": "COMPLETED",
      "created_at": "2023-10-27T10:00:00",
      "updated_at": "2023-10-27T10:05:00"
    }
  ]
}
```

---

## 3. Get User Jobs
Retrieves a list of jobs submitted by a specific user.

- **Endpoint**: `GET /jobs/user/{user_id}`

### Response (200 OK)
- Returns the same array structure as `Get All Jobs` but filtered by the provided `user_id`.

---

## 4. Download File
Downloads a specific file (CV, Job Description, or Report) related to a job.

- **Endpoint**: `GET /jobs/files`
- **Query Parameters**:
  - `path`: The absolute path of the file to download (provided in the `Get All Jobs` response).

### Example
`GET /jobs/files?path=uploads/550e8400-e29b-41d4-a716-446655440000/cv_resume.pdf`

### Response
- **Headers**: 
  - `Content-Type`: `application/pdf` (or `application/json`, etc.)
  - `Content-Disposition`: `attachment; filename="cv_resume.pdf"`
- **Body**: Binary file content.
