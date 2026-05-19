from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9가-힣._ -]+")


def ensure_storage(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    name = SAFE_NAME_PATTERN.sub("_", name)
    return name or "uploaded.xlsx"


def is_excel_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def unique_destination(directory: Path, filename: str) -> Path:
    destination = directory / sanitize_filename(filename)
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    for index in range(1, 1000):
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate

    raise RuntimeError("같은 이름의 파일이 너무 많습니다.")


def save_uploaded_file(upload_dir: Path, uploaded_file) -> Path:
    if not is_excel_file(uploaded_file.name):
        raise ValueError("xlsx 또는 xls 파일만 업로드할 수 있습니다.")

    destination = unique_destination(upload_dir, uploaded_file.name)
    with destination.open("wb") as file:
        file.write(uploaded_file.getbuffer())
    return destination


def list_excel_files(upload_dir: Path) -> list[Path]:
    if not upload_dir.exists():
        return []
    return sorted(
        [
            path
            for path in upload_dir.iterdir()
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
        ],
        key=lambda path: path.name.lower(),
    )


def delete_file(upload_dir: Path, filename: str) -> bool:
    safe_name = sanitize_filename(filename)
    target = (upload_dir / safe_name).resolve()
    upload_root = upload_dir.resolve()

    if upload_root not in target.parents:
        raise ValueError("업로드 폴더 밖의 파일은 삭제할 수 없습니다.")
    if target.exists() and target.is_file():
        target.unlink()
        return True
    return False

