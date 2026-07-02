# DECIMER Document Processing Pipeline

A modular, production-ready pipeline for extracting chemical structure images from PDF documents and converting them into **SMILES** using DECIMER.

---

# Features

- PDF document ingestion
- Accepts PDF **file paths** or **binary blobs**
- Deterministic SHA-256 Document IDs
- High-resolution PDF rendering
- Chemical structure detection using YOLO
- Automatic image cropping
- Image preprocessing
- Chemical structure recognition using DECIMER
- Metadata generation
- CSV export
- Docker-ready architecture
- Modular pipeline for easy integration into APIs and automation platforms

---

# Pipeline Architecture

```
                PDF Input
           (Path or Blob)
                   │
                   ▼
        Generate Document ID
                   │
                   ▼
        Create Output Structure
                   │
                   ▼
        Register Document
                   │
                   ▼
          Render PDF Pages
                   │
                   ▼
      Detect Chemical Structures
                (YOLO)
                   │
                   ▼
          Crop Structures
                   │
                   ▼
        Image Preprocessing
                   │
                   ▼
            Run DECIMER
                   │
                   ▼
         Generate Metadata
                   │
                   ▼
             Export CSV
```

---

# Project Structure

```
project/

│
├── config.py
├── main.py
├── pipeline.py
├── hashing.py
├── inventory.py
├── metadata.py
├── renderer.py
├── segmentation.py
├── processor.py
├── storage.py
├── decimer.py
├── requirements.txt
├── Dockerfile
│
├── outputs/
│
└── models/
    └── yolo/
        └── best.pt
```

---

# Output Structure

Each processed PDF receives its own directory.

```
outputs/

    <document_id>/

        metadata.csv

        process.log

        page_001/

            raw/
                page.png

            crops/
                image_001.png
                image_002.png

            cleaned/
                image_001.png
                image_002.png

        page_002/

        page_003/
```

---

# Metadata

Each detected structure is stored as one row.

| Column |
|---------|
| document_id |
| pdf_name |
| page_number |
| image_id |
| image_path |
| clean_image_path |
| image_type |
| is_formula |
| confidence |
| bbox |
| smiles |
| processing_status |
| error_message |

---

# Input Modes

## File Path

```python
from pipeline import Pipeline

pipeline = Pipeline()

pipeline.run("papers/example.pdf")
```

---

## Binary Blob

```python
from pipeline import Pipeline

with open("paper.pdf", "rb") as f:
    pdf = f.read()

pipeline = Pipeline()

pipeline.run(pdf)
```

---

# Installation

Clone the repository

```bash
git clone <repository_url>

cd project
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

Run

```bash
python main.py
```

Enter the PDF path when prompted.

Example

```
Enter the full path to the PDF file:

D:\Research\paper.pdf
```

---

# Docker

Build the container

```bash
docker build -t decimer-pipeline .
```

Run

```bash
docker run decimer-pipeline
```

(Additional volume mounts and runtime arguments can be added depending on your deployment environment.)

---

# Workflow

1. Read PDF
2. Generate SHA-256 document ID
3. Create document output folder
4. Render PDF pages
5. Detect chemical structures
6. Crop detected structures
7. Clean images
8. Run DECIMER
9. Generate metadata
10. Export CSV

---

# Technologies Used

- Python 3.12+
- PyMuPDF
- OpenCV
- Ultralytics YOLO
- DECIMER
- Pandas
- NumPy
- Docker

---

# Design Principles

- Modular architecture
- Separation of concerns
- Deterministic document identification
- Production-ready code organization
- Docker-first deployment
- API-friendly interface
- Easy integration with workflow automation tools (e.g., Workato)

---

# Future Improvements

- FastAPI service
- Batch PDF processing
- Multi-threaded rendering
- GPU inference support
- Cloud storage integration
- REST API endpoints
- Confidence threshold tuning
- Automatic retry and recovery
- Structured logging and monitoring

---

# License

This project is intended for research and educational purposes unless otherwise specified.