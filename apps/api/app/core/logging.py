import logging


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    # Provider URLs can contain API tokens in query parameters. Keep httpx from
    # writing those URLs into local or hosted logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
