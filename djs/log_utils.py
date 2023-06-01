from orjson import orjson, dumps

import logging
from logging.config import dictConfig

import structlog


def proc_id_processor(logger, method_name: str, event_dict: dict):
    event_dict["process_identifier"] = f"djs-operator@1.0.0"
    return event_dict


LOG_LEVEL = "INFO"  # TODO: Read from env

LOG_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    proc_id_processor,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.dict_tracebacks,
    structlog.processors.format_exc_info,
]

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(
                serializer=dumps, option=orjson.OPT_UTC_Z
            ),
            "foreign_pre_chain": LOG_PROCESSORS
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": LOG_LEVEL
        }
    }
}


def setup_logging():
    dictConfig(LOG_CONFIG)
    logging.captureWarnings(True)

    structlog.reset_defaults()
    structlog.configure(
        processors=[
            *LOG_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )
