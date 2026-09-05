# Smiles Chem Transformer Agent

> **Domain:** Computational Biology & AI Drug Discovery  
> **Reference Guidelines & Standards:** `wwPDB, IUPAC & CLSI Computational Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Smiles Chem Transformer Agent** is an advanced analytical and computational platform implementing Molecular Kekule valence, tautomer enumerator & InChI canonicalizer. It provides:

- **Multi-Agent Evaluation**: Specialized workers for QC invariant checking, safety escalation, and protocol conformance
- **Zero-PHI Outbound Guard**: AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **HMAC-SHA256 Audit Trail**: Cryptographically signed, tamper-evident logs for every evaluation
- **FastAPI REST API**: OpenAPI 3.1 endpoints for integration with external systems

---

## 🚀 Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/smiles-chem-transformer-agent.git
cd smiles-chem-transformer-agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Configure environment
cp .env.example .env
# Edit .env to set a secure AUDIT_SECRET_KEY
```

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection
- **Batch Processing**: CSV-based high-throughput task evaluation

---

## 💻 CLI Quickstart & Usage

### 1. Run Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 4. Batch Process CSV File
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task identifier | `TASK-2026-001` |
| `--target` | Target identifier | `KEY-TARGET-01` |
| `--primary` | Primary metric value | `28.5` |
| `--secondary` | Secondary metric value | `14.2` |
| `--critical` | Enable critical flag | `False` |
| `--status` | Status descriptor | `DISCORDANT` |

### Input Data Schema (CSV)
| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary kinetic/confidence score | Optional |
| `is_critical_flag` | Emergency escalation trigger | Optional |
| `status_descriptor` | Status code or phenotype | Optional |

---

## 🌐 REST API Endpoints

When the server is running (default: http://127.0.0.1:8000):

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Health check and system metadata |
| `/metrics` | GET | Prometheus operational metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Query supervisory chat |
| `/api/audit/logs` | GET | Retrieve HMAC audit trail |

### Example API Request
```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK-001",
    "target_identifier": "TARGET-01",
    "primary_metric": 28.5,
    "secondary_metric": 14.2,
    "status_descriptor": "DISCORDANT",
    "is_critical_flag": true
  }'
```

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`)

### Security Configuration

The `AUDIT_SECRET_KEY` environment variable **must** be set in production. Generate a secure key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

### Docker Compose (Recommended)
```bash
# Set your production secret key
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Start services
docker-compose up -d
```

### Docker Direct
```bash
docker build -t smiles-chem-transformer-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key smiles-chem-transformer-agent
```

---

## 📁 Project Structure

```
smiles-chem-transformer-agent/
├── agents/                    # Core agent modules
│   ├── api.py                 # FastAPI REST server
│   ├── base.py                # Security guards, audit trail
│   ├── models.py              # Pydantic data models
│   ├── supervisor.py          # Master coordinator
│   ├── workers.py             # Specialized domain workers
│   ├── llm_factory.py         # LLM provider factory
│   ├── metrics.py             # Prometheus metrics
│   ├── learning.py            # Bayesian calibration
│   └── streamer.py            # WebSocket telemetry
├── smiles_transformer/        # SMILES transformer package
│   ├── engine.py              # Core algorithmic engine
│   ├── agents.py              # Sub-agent implementations
│   ├── models.py              # Data models
│   ├── server.py              # FastAPI server
│   └── cli.py                 # CLI interface
├── tests/                     # Test suite
├── web/                       # Web dashboard
├── cli.py                     # Main CLI entry point
├── simulator.py               # High-throughput simulator
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-service orchestration
└── .github/workflows/ci.yml   # CI/CD pipeline
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
