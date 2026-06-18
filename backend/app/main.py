from fastapi import FastAPI

app = FastAPI(title="A Story of Two — Generation Backend")


@app.get("/health")
def health() -> dict:
    return {"ok": True}
