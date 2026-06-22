# Assignment: CI/CD Fundamentals with a Python Web API

**Estimated time: 2 hours** (broken into timed sections below)
**Framework: choose FastAPI *or* Flask** — both starter snippets are provided in the Appendix.

---

## Learning Objectives

By the end of this assignment, you will be able to:

1. Explain the difference between Continuous Integration (CI) and Continuous Delivery/Deployment (CD).
2. Write automated unit tests for a Python web API using `pytest`.
3. Add a linting/formatting quality gate to a project.
4. Configure a GitHub Actions workflow that automatically runs tests on every push.
5. Add a second pipeline stage that simulates a deployment step, and explain why it depends on the test stage passing first.

## Prerequisites

- Python 3.10+ installed
- A GitHub account
- Basic familiarity with git (`clone`, `add`, `commit`, `push`) and the command line
- A code editor (VS Code recommended)

## Scenario

You're given a tiny **Task Manager API** with three endpoints: a health check, a way to list tasks, and a way to create a task. Your job isn't to build new features — it's to wrap this existing app in a working CI/CD pipeline.

---

## Part 0 — Setup (15 minutes)

1. Create a new GitHub repository (public is fine, it's free for Actions).
2. Copy the starter code for your chosen framework from the Appendix into `main.py` (or `app.py` for Flask), along with the matching `requirements.txt`.
3. Create and activate a virtual environment, then install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Run the app locally and confirm it works by hitting the endpoints (browser, `curl`, or the framework's interactive docs at `/docs` for FastAPI).
5. Commit and push this working baseline to GitHub before moving on.

**Checkpoint:** the app runs locally and you have an initial commit on GitHub.

## Part 1 — Write the Tests (30 minutes)

Create `test_main.py`. Using `pytest` (and `httpx`/`TestClient` for FastAPI, or Flask's built-in test client for Flask), write **at least 4 tests**:

- `GET /health` returns a 200 status code.
- `POST /tasks` with a valid payload returns a 201 status code and the created task in the response.
- `GET /tasks` returns a list, and the list grows after a task is created.
- One test of your choosing that checks a failure case (e.g., missing required field returns a 4xx error).

Run them locally with `pytest -v` until all four pass. Commit and push.

**Checkpoint:** `pytest -v` shows 4+ passing tests, committed to GitHub.

## Part 2 — Local Quality Gate: Linting (15 minutes)

Before automating anything, run the same checks a pipeline would run, by hand:

```bash
pip install flake8 black
black --check .
flake8 .
```

Fix any formatting or style issues `black`/`flake8` flag (running `black .` without `--check` will auto-format for you). This step exists so that you understand *what* the pipeline will be checking before you automate it — a CI pipeline is just "the checks you'd run locally, run automatically by a server instead."

**Checkpoint:** `black --check .` and `flake8 .` both pass with no errors. Commit and push.

## Part 3 — Build the CI Pipeline with GitHub Actions (45 minutes)

Create the file `.github/workflows/ci.yml`. A partially-filled skeleton is in the Appendix — fill in the blanks marked `___`. Your workflow must:

1. Trigger on `push` and `pull_request` to the `main` branch.
2. Check out the code and set up Python.
3. Install dependencies from `requirements.txt`.
4. Run `flake8` and `black --check` as a lint step.
5. Run `pytest` as a test step.

Push your completed workflow file, then:

- Go to the **Actions** tab on GitHub and confirm the workflow runs and **passes** (all green).
- Intentionally break something — comment out an assertion in one test, or introduce a formatting issue — commit, and push. Watch the pipeline **fail**.
- Fix the issue, commit, push again, and confirm it goes back to green.

This failure-then-fix cycle is the actual point of the exercise: you should see, with your own eyes, that the pipeline catches a real problem before it would have reached anyone else.

**Checkpoint:** screenshot of one red (failed) run and one green (passed) run in your Actions tab.

## Part 4 — Add a Simulated Deployment Stage (15 minutes)

Real CD usually pushes to a server, container registry, or hosting platform. We're simulating that step so the assignment doesn't depend on external accounts or cloud credentials.

Add a second job called `deploy` to your workflow with these properties:

- It only runs on pushes to `main` (not on pull requests).
- It uses `needs: test` (or whatever you named your first job) so it **only runs if the test job succeeds**.
- Its only step echoes a message like `"Deploying version $(git rev-parse --short HEAD) to production..."`.

Push this change and confirm in the Actions tab that the `deploy` job only appears/runs after `test` succeeds, and that it would be skipped if `test` failed.

**Checkpoint:** Actions tab shows two sequential jobs, `test` then `deploy`, with `deploy` gated on `test` passing.

## Wrap-Up (10 minutes)

Write a short reflection (3–5 sentences) in a `REFLECTION.md` file answering:

- What does each stage of your pipeline (lint, test, deploy) actually protect against?
- Why does the order matter — what could go wrong if `deploy` ran before `test`?
- What's one thing you'd add to make this pipeline closer to a real production setup?

---

## Submission

Submit a link to your GitHub repository containing:

1. Working application code and `requirements.txt`
2. `test_main.py` with 4+ passing tests
3. `.github/workflows/ci.yml` with both the `test` and `deploy` jobs
4. A screenshot (or two) from the Actions tab showing a failed run and a passing run
5. `REFLECTION.md`

## Grading Rubric (100 points)

| Component | Points | Criteria |
|---|---|---|
| App runs locally | 10 | Starter app works unmodified |
| Tests | 25 | 4+ meaningful tests, all passing |
| Lint/format gate | 10 | `flake8` and `black --check` pass cleanly |
| CI workflow triggers correctly | 15 | Runs on push and pull_request to main |
| CI workflow installs deps, lints, tests | 20 | All three steps present and correctly ordered |
| Deploy job gated on test job | 15 | Uses `needs:`, runs only on main, only after tests pass |
| Reflection | 5 | Answers all three questions thoughtfully |

---

## Optional Bonus Challenges (not required, not time-boxed)

If you finish early or want to go further on your own time:

- Containerize the app with a `Dockerfile` and add a job that builds the image.
- Add a test matrix that runs your tests on Python 3.10, 3.11, and 3.12.
- Turn on a GitHub branch protection rule requiring the CI workflow to pass before merging to `main`.
- Replace the simulated deploy step with a real deployment to a free-tier host (e.g., Render or Railway) using a deploy hook or API key stored as a GitHub Secret.

---

## Appendix: Starter Code

### Option A — FastAPI

**`main.py`**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
tasks = []


class Task(BaseModel):
    title: str
    done: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    tasks.append(task.dict())
    return task
```

**`requirements.txt`**
```
fastapi
uvicorn[standard]
pytest
httpx
```

**Run locally:** `uvicorn main:app --reload`

**Test skeleton (`test_main.py`)**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    # TODO: assert status code is 200
    pass


def test_create_task():
    # TODO: POST to /tasks with a title, assert 201 and correct response body
    pass


def test_get_tasks_grows():
    # TODO: assert /tasks returns a list and it includes the task you just created
    pass


def test_create_task_empty_title_fails():
    # TODO: POST with an empty title, assert a 4xx error
    pass
```

### Option B — Flask

**`app.py`**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
tasks = []


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    task = {"title": title, "done": data.get("done", False)}
    tasks.append(task)
    return jsonify(task), 201


if __name__ == "__main__":
    app.run(debug=True)
```

**`requirements.txt`**
```
flask
pytest
```

**Run locally:** `python app.py`

**Test skeleton (`test_main.py`)**
```python
import pytest
from app import app


@pytest.fixture
def client():
    return app.test_client()


def test_health(client):
    # TODO: assert status code is 200
    pass


def test_create_task(client):
    # TODO: POST JSON {"title": "Write tests"} to /tasks, assert 201
    pass


def test_get_tasks_grows(client):
    # TODO: assert /tasks returns a list and it includes the task you just created
    pass


def test_create_task_empty_title_fails(client):
    # TODO: POST with an empty title, assert a 4xx error
    pass
```

### GitHub Actions Workflow Skeleton

Save as `.github/workflows/ci.yml`. Fill in every `___`.

```yaml
name: ___

on:
  push:
    branches: [___]
  pull_request:
    branches: [___]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@___

      - name: Set up Python
        uses: actions/setup-python@___
        with:
          python-version: "___"

      - name: Install dependencies
        run: |
          pip install -r ___

      - name: Lint
        run: |
          ___
          ___

      - name: Run tests
        run: ___

  deploy:
    runs-on: ubuntu-latest
    needs: ___
    if: github.ref == 'refs/heads/___' && github.event_name == '___'
    steps:
      - name: Simulate deployment
        run: echo "Deploying version $(___) to production..."
```
