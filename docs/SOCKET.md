# WebSocket Documentation

## Overview
The WebSocket API is used to stream real-time progress updates for a specific job application processing. The client initiates a connection specifically for a `job_id` and listens for events.

## Connection
**URL**: `ws://<host>:<port>/ws/jobs/{job_id}`  
**Example**: `ws://localhost:8000/ws/jobs/550e8400-e29b-41d4-a716-446655440000`

### Behavior
- **One-way Communication**: The server streams updates to the client. The client does not need to send messages to the server.
- **Single Connection**: Only one active connection is maintained per `job_id`. New connections will supersede old ones.

## Events

### 1. Connection Established
Sent immediately upon successful connection.

```json
{
  "type": "CONNECTION_ESTABLISHED",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Connected to job stream"
}
```

### 2. Progress Update
Sent periodically as the job progresses through different pipeline stages (e.g., Parsing, Cleaning, Matching).

```json
{
  "type": "PROGRESS",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Parsing CV...",
  "progress": 20
}
```

### 3. Completion
Sent when the job is fully processed.

```json
{
  "type": "PROGRESS",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Evaluation Complete",
  "progress": 100
}
```

### 4. Error
Sent if an exception occurs during processing.

```json
{
  "type": "PROGRESS",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error: File format not supported",
  "progress": 0
}
```
