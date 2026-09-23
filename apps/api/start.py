"""Railway entrypoint that reads the assigned port in Python.

Railway's custom start command can pass ``$PORT`` literally when it is
configured as an exec-style command. Reading the environment here avoids
shell interpolation entirely while still honoring Railway's assigned port.
"""

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
