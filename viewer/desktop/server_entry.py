from __future__ import annotations

import os
import socket
from pathlib import Path

import uvicorn

from app.main import app


def main() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    Path(os.environ["WIKI_DESKTOP_PORT_FILE"]).write_text(str(port), encoding="ascii")
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
        loop="asyncio",
        http="h11",
    )
    uvicorn.Server(config).run(sockets=[listener])


if __name__ == "__main__":
    main()
