"""Read-only optional loopback health endpoint; no remote tool execution."""
from fastapi import FastAPI
from . import __version__
app = FastAPI(title='Sheikh Hamamomin local health')

@app.get('/health')
def health():
    return {'status': 'ok', 'version': __version__, 'tools_exposed': False}

# Run: uvicorn hamamomin.service:app --host 127.0.0.1 --port 8765
