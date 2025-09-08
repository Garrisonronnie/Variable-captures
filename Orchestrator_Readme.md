# 🛠️ Python Utility Orchestrator

A **production-ready orchestration tool** to run shell/Python scripts with:
- ✅ Dependency-aware DAG execution
- ✅ Parallel execution
- ✅ Retry logic with backoff
- ✅ Rich progress UI via `rich`
- ✅ Logging + dashboard
- ✅ CLI integration

---

## 📦 Features

- 📂 **`build.yaml`** support (define script dependencies)
- 🧠 **Smart retries** with exponential backoff
- 🚦 **Parallel** or **sequential** execution
- 📊 Live **dashboard** (CLI + JSON)
- 📜 Supports `.py`, `.sh`, `.bash` scripts

---

## 📁 Folder Structure

```text
.
├── orchestrator.py       # Main utility
├── build.yaml            # Script dependency DAG
├── scripts/              # Your scripts (.py/.sh)
│   ├── setup.sh
│   └── cleanup.py
├── logs/                 # Logs and dashboard
│   └── build.log
├── LICENSE
├── README.md
└── .gitignore