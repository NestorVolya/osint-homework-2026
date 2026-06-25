import json
import zipfile
from pathlib import Path
from datetime import datetime


def create_run_dir(base_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = base_dir / ts
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    (run_dir / "report").mkdir(exist_ok=True)
    return run_dir


def save_raw_json(run_dir: Path, name: str, data: dict | list) -> Path:
    path = run_dir / "raw" / f"{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_raw_bytes(run_dir: Path, name: str, data: bytes) -> Path:
    path = run_dir / "raw" / name
    path.write_bytes(data)
    return path


def zip_run(run_dir: Path) -> Path:
    zip_path = run_dir.parent / f"{run_dir.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in run_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(run_dir.parent))
    return zip_path
