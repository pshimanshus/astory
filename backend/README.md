# A Story of Two — Generation Backend

## Setup
    cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

Add to repo-root `.env.local`: `OPENAI_API_KEY=...` and `GEMINI_API_KEY=...`

## Run
    . .venv/bin/activate && uvicorn app.main:app --reload

## Test
    . .venv/bin/activate && python3 -m unittest
