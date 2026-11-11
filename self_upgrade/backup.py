from pathlib import Path
from datetime import datetime
import shutil


BACKUP_DIR = Path("backups")


def backup_file(file_path: str) -> str:
    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.name}.{timestamp}.bak"
    destination = BACKUP_DIR / backup_name

    shutil.copy2(source, destination)
    return str(destination)