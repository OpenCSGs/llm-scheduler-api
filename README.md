# LLM Scheduler API

## Prerequisite
Slurm engine was installed. Reference: [Slurm Installation](./docs/slurm_install.md)
## Installation

1. Install dependency：
Python 3.10+
```bash
pip install -r requirements.txt
```

2. API

```bash
python main.py
```
or 

```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

## API document
http://localhost:3000/docs

