# Persona-Driven Document Intelligence 📄🧠

## 🚀 Overview

This project builds an intelligent document analysis system that extracts and ranks the most relevant sections from a collection of PDF documents based on a specific **persona** and their **job-to-be-done**.

It is designed to be:
- ✅ CPU-only (no GPU dependencies)
- ✅ Offline-compatible (no internet access)
- ✅ Dockerized and platform-specific (`linux/amd64`)
- ✅ Efficient (runs under 60s for 3–5 documents)

---

## 🧠 How It Works

### Input
The system takes:
- A collection of **PDF documents**
- A **persona** with a specific role/expertise
- A **job-to-be-done** or task they want to accomplish

Example (from `input/sample_input.json`):

```json
{
  "documents": [
    { "filename": "Dinner Ideas - Mains_1.pdf" },
    { "filename": "Dinner Ideas - Sides_2.pdf" }
  ],
  "persona": {
    "role": "Chef exploring new menu ideas"
  },
  "job_to_be_done": {
    "task": "Identify creative and trending dishes for the fall season"
  }
}

Build Docker Image
docker build --platform linux/amd64 -t persona-intelligence .
▶ Run the Solution
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  persona-intelligence
