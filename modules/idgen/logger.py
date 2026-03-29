import logging
from pathlib import Path
from datetime import datetime


def setup_logger():
    """
    Setup logger for ID Generator.
    Logs to both file and console.
    """
    # Create logs directory
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Log file with date
    log_file = log_dir / f"idgen_{datetime.now().strftime('%Y%m%d')}.log"

    # Create logger
    logger = logging.getLogger('IDGenerator')
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler (optional - only errors)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
