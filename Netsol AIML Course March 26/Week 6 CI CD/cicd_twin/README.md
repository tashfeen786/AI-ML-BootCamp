# CI/CD Pipeline Digital Twin
### A scenario-based interactive simulator for learning CI/CD concepts

---

## Quick Start (macOS)

**Option 1 — Terminal (recommended):**
```bash
cd cicd_twin
bash launch.sh
```

**Option 2 — Manual:**
```bash
cd cicd_twin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open: **http://localhost:5050**

---

## What's Included

### 5 Learning Scenarios

| # | Scenario | What students learn |
|---|----------|-------------------|
| 1 | **Happy Path** | Full 6-stage pipeline: commit → build → lint → test → docker → deploy |
| 2 | **Test Failure** | A bug causes 2/5 tests to fail — pipeline stops before deployment |
| 3 | **Lint Failure** | Working code rejected for style violations (flake8) |
| 4 | **Build Failure** | Typo in requirements.txt crashes the build at Stage 2 |
| 5 | **Deploy & Rollback** | Health check fails post-deploy — automatic rollback triggers |

### Features
- **Real-time terminal output** — streams line by line like a real CI runner
- **Syntax-highlighted code editor** — shows the relevant file for each stage
- **Step mode** — advance one stage at a time to pause and discuss
- **Speed control** — slow (0.5×) for beginners, fast (4×) for demos
- **Learning panel** — explains what each stage does and why it matters
- **Fail overlays** — when a stage fails, shows what broke and how to fix it

---

## Project Structure

```
cicd_twin/
├── app.py                  ← Flask + SocketIO backend
├── requirements.txt        ← Python dependencies
├── launch.sh               ← macOS launcher script
├── README.md               ← This file
├── templates/
│   └── index.html          ← Full frontend (HTML + CSS + JS)
└── scenarios/
    └── scenarios.json      ← All 5 scenarios with code and terminal output
```

---

## Adding Your Own Scenarios

Edit `scenarios/scenarios.json`. Each scenario has:

```json
{
  "id":          "my_scenario",
  "title":       "Scenario 6 — My Custom Scenario",
  "subtitle":    "What goes wrong",
  "description": "Full description shown in the learn panel",
  "difficulty":  "Beginner",
  "color":       "#059669",
  "icon":        "🔧",
  "tags":        ["tag1", "tag2"],
  "files": {
    "app.py": "...file contents...",
    "requirements.txt": "..."
  },
  "stages": [
    {
      "id":      "commit",
      "name":    "Code Commit",
      "icon":    "💻",
      "outcome": "pass",
      "file":    "app.py",
      "file_highlight": -1,
      "learn":   "Explanation for students (HTML allowed)",
      "terminal_lines": [
        {"text": "$ git push origin main", "type": "cmd",  "delay": 0.4},
        {"text": "Pipeline triggered!",    "type": "ok",   "delay": 0.3},
        {"text": "Some info",              "type": "info", "delay": 0.2},
        {"text": "A warning",             "type": "warn", "delay": 0.2},
        {"text": "An error",              "type": "err",  "delay": 0.2}
      ],
      "fail_message": "Short description of what failed",
      "fail_learn": "How to fix this (shown in the overlay)"
    }
  ]
}
```

**Terminal line types:** `cmd`, `ok`, `err`, `warn`, `info`, `dim`

**Stage outcomes:** `"pass"` or `"fail"` (pipeline stops on fail)

---

## Requirements

- Python 3.9 or higher
- macOS, Linux, or Windows (with Git Bash for launch.sh)
- No internet connection needed after first install
- Modern browser (Safari, Chrome, Firefox)
