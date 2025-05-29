# Scout Agent PoC

Lightweight monitoring assistant that accepts NL instructions, stores tasks in SQLite, and periodically scrapes web pages to detect changes.

## Project Setup

```bash
git clone <your-repo-url>
cd scout_agent_poc
python3.10 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
