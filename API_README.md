# API Documentation for Verta (Serve.py)

This API is designed to handle user input through Verta and return responses, with support for both streaming and non-streaming modes.

## Base URL

```
http://localhost:80
```

## Endpoints

### 1. `/initialize`

**Method:** `GET`

**Description:** Initializes the vector store retriever for a specific product (ASIN) and user ID. This process caches the review and metadata for efficient future queries.

**Query Parameters:**

| Parameter | Type | Description |
| --- | --- | --- |
| asin | string | The product's Parent ASIN ID. |
| user_id | int | The unique identifier for the user. |

**Response:**

```json
{
  "status": "retriever initialized",
  "asin": "string",
  "user_id": "integer"
}

```

---

### 2. `/clear-cache`

**Method:** `POST`

**Description:** Clears the vector store and metadata cache for a specified product (ASIN) and user ID.

**Request Body:**

```json
{
  "user_id": "string",
  "parent_asin": "string"
}

```

| Field | Type | Description |
| --- | --- | --- |
| user_id | string | The unique identifier for the user. |
| parent_asin | string | The product's Parent ASIN ID. |

**Response:**

```json
json
Copy code
{
  "status": "cache cleared"
}

```

Returns **400 Bad Request** if the specified retriever does not exist.

---

### 3. `/dev-invoke`

**Method:** `POST`

**Description:** Invokes the agent with the given user input and retrieves a complete response (non-streaming).

**Request Body:**

```json
{
  "user_input": "string",
  "config": {
    "configurable": {
        "thread_id": "string"
    }
  },
  "parent_asin": "string",
  "user_id": "string",
  "log_langfuse": true,
  "stream_tokens": false
}
```

| Field          | Type   | Description                                                        |
|----------------|--------|--------------------------------------------------------------------|
| user_input     | string | The question or query you want the agent to respond to.            |
| config         | dict   | Configuration for agent callbacks and threading.                   |
| parent_asin    | string | The Parent Asin Id of the product querying.                        |  
| user_id        | string | The User-ID of the user logged in.                                 |
| log_langfuse   | bool   | Whether to log responses and interactions to Langfuse.             |
| stream_tokens  | bool   | If true, streaming tokens are used; otherwise, a full response is returned. (No use in invoke method)|

**Response:**

```json
{
  "question": "string",
  "answer": "string",
  "followup_questions": [
    "string",
    "string",
    "string"
  ]
}
```

| Field             | Type   | Description                                                            |
|-------------------|--------|------------------------------------------------------------------------|
| question          | string | The user query or question submitted.                                   |
| answer            | string | The agent's full response.                                              |
| followup_questions| array  | Suggested follow-up questions based on the answer.                      |

---

### 4. `/dev-stream`

**Method:** `POST`

**Description:** Streams the agent's response to a user input, including intermediate messages and tokens.

**Request Body:**

```json
{
  "user_input": "string",
  "config": {
    "configurable": {
        "thread_id": "string"
    }
  },
  "parent_asin": "string",
  "user_id": "string",
  "log_langfuse": true,
  "stream_tokens": true
}
```

| Field          | Type   | Description                                                        |
|----------------|--------|--------------------------------------------------------------------|
| user_input     | string | The question or query you want the agent to respond to.            |
| config         | dict   | Configuration for agent callbacks and threading.                   |
| parent_asin    | string | The Parent Asin Id of the product querying.                        |  
| user_id        | string | The User-ID of the user logged in.                                 |
| log_langfuse   | bool   | Whether to log responses and interactions to Langfuse.             |
| stream_tokens  | bool   | If true, token-by-token responses are streamed.                    |

**Response:**

Streams intermediate responses and tokens (if `stream_tokens` is set to `True`). The final message contains the full answer and associated citations.

Example:

``` json
data: {"type": "token", "content": "Hello "}
data: {"type": "token", "content": "World"}
data: {"type": "message", "content": {
    "question": "string",
    "answer": "string",
    "followup_questions": [
      "string",
      "string",
      "string"
    ]
  }
}
data: [DONE]
```

---

### Usage Examples

**Invoke Example (cURL):**

```bash
curl -X POST "http://localhost:80/invoke" -H "Content-Type: application/json" -d '{
  "user_input": "Explain how to motivate a grade 2 student.",
  "config": {"thread_id": "2"},
  "log_langfuse": 1,
  "stream_tokens": 0
}'
```

**Stream Example (cURL):**

```bash
curl -X POST "http://localhost:80/stream" -H "Content-Type: application/json" -d '{
  "user_input": "How to plan a lesson on fractions?",
  "config": {"thread_id": "2"},
  "log_langfuse": 1,
  "stream_tokens": 1
}' --no-buffer
```

---

### Error Handling

- **500 Internal Server Error:** When the agent encounters an issue processing the input.
- **400 Bad Request:** When the input is improperly formatted.

---

### Installation and Setup

Refer to the main `README.md` for installation and setup instructions.

---

### Notes

- Ensure that environment variables for `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` are properly set.
- For tracing and monitoring, Langfuse integration is used for logging interactions and responses.