from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_KEY_CANDIDATES = [
    "비용명",
    "표항목",
    "항목명",
    "항목",
    "item",
    "Item",
    "parameter",
    "Parameter",
    "name",
    "Name",
]

NON_AVERAGE_COLUMNS = {"비용코드"}

MULTI_ROW_HEADER_KEYWORDS = {
    "계획예산",
    "실행예산",
    "전년도집행",
    "당년도예산",
    "당년도집행",
    "가집행금액",
    "당해누계",
    "집행계",
    "예산잔액",
}


@dataclass(frozen=True)
class WorkbookPreview:
    filename: str
    sheet_name: str
    columns: list[str]
    row_count: int


@dataclass(frozen=True)
class ProcessResult:
    output_path: Path
    input_files: list[str]
    key_column: str
    numeric_columns: list[str]
    text_columns: list[str]
    input_rows: int
    output_rows: int


def _clean_label(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _deduplicate_columns(columns: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    result: list[str] = []
    for column in columns:
        base = column or "컬럼"
        counts[base] = counts.get(base, 0) + 1
        if counts[base] == 1:
            result.append(base)
        else:
            result.append(f"{base}_{counts[base]}")
    return result


def _looks_like_two_row_header(raw: pd.DataFrame) -> bool:
    if len(raw) < 3:
        return False
    first_row = {_clean_label(value) for value in raw.iloc[0].tolist()}
    return bool(first_row.intersection(MULTI_ROW_HEADER_KEYWORDS))


def _build_two_row_headers(raw: pd.DataFrame) -> list[str]:
    first = [_clean_label(value) for value in raw.iloc[0].tolist()]
    second = [_clean_label(value) for value in raw.iloc[1].tolist()]
    columns: list[str] = []
    current_top = ""

    for index, (top, child) in enumerate(zip(first, second)):
        if index == 0:
            columns.append("비목분류")
        elif index == 1:
            columns.append("비용코드")
        elif index == 2:
            columns.append("비용명")
        else:
            if top:
                current_top = top
            parent = top or current_top
            if parent and child:
                columns.append(f"{parent}_{child}")
            else:
                columns.append(parent or child or f"컬럼{index + 1}")

    return _deduplicate_columns(columns)


def read_first_sheet(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=0, header=None)
    if _looks_like_two_row_header(raw):
        columns = _build_two_row_headers(raw)
        frame = raw.iloc[2:].copy()
        frame.columns = columns
    else:
        frame = pd.read_excel(path, sheet_name=0)

    frame = frame.dropna(how="all").reset_index(drop=True)
    if "비목분류" in frame.columns:
        frame["비목분류"] = frame["비목분류"].ffill()
    return frame


def preview_workbook(path: Path) -> WorkbookPreview:
    excel = pd.ExcelFile(path)
    sheet_name = excel.sheet_names[0]
    frame = read_first_sheet(path).head(20)
    return WorkbookPreview(
        filename=path.name,
        sheet_name=sheet_name,
        columns=[str(column) for column in frame.columns],
        row_count=int(len(read_first_sheet(path))),
    )


def validate_same_columns(frames: list[pd.DataFrame], filenames: list[str]) -> list[str]:
    if not frames:
        raise ValueError("처리할 엑셀 파일이 없습니다.")

    reference = [str(column) for column in frames[0].columns]
    mismatches: list[str] = []
    for filename, frame in zip(filenames, frames):
        columns = [str(column) for column in frame.columns]
        if columns != reference:
            mismatches.append(filename)
    return mismatches


def choose_key_column(columns: list[str], requested_key: str | None = None) -> str:
    if requested_key and requested_key in columns:
        return requested_key
    for candidate in DEFAULT_KEY_CANDIDATES:
        if candidate in columns:
            return candidate
    return columns[0]


def merge_excel_average(
    files: list[Path],
    output_dir: Path,
    key_column: str | None = None,
    output_name: str = "merged_average.xlsx",
) -> ProcessResult:
    if not files:
        raise ValueError("업로드된 엑셀 파일이 없습니다.")

    frames = [read_first_sheet(path) for path in files]
    filenames = [path.name for path in files]
    mismatches = validate_same_columns(frames, filenames)
    if mismatches:
        joined = ", ".join(mismatches)
        raise ValueError(f"컬럼 구조가 다른 파일이 있습니다: {joined}")

    columns = [str(column) for column in frames[0].columns]
    selected_key = choose_key_column(columns, key_column)
    combined = pd.concat(frames, ignore_index=True)

    if selected_key not in combined.columns:
        raise ValueError(f"기준 컬럼을 찾을 수 없습니다: {selected_key}")

    combined = combined[combined[selected_key].notna()].copy()
    combined[selected_key] = combined[selected_key].astype(str).str.strip()
    combined = combined[combined[selected_key] != ""]

    for column in combined.columns:
        if column != selected_key:
            converted = pd.to_numeric(combined[column], errors="coerce")
            if converted.notna().any():
                combined[column] = converted

    numeric_columns = [
        column
        for column in combined.columns.tolist()
        if column != selected_key
        and column not in NON_AVERAGE_COLUMNS
        and pd.api.types.is_numeric_dtype(combined[column])
    ]
    text_columns = [
        column
        for column in combined.columns.tolist()
        if column not in numeric_columns and column != selected_key
    ]

    aggregation: dict[str, str] = {column: "mean" for column in numeric_columns}
    aggregation.update({column: "first" for column in text_columns})

    if aggregation:
        result = combined.groupby(selected_key, dropna=False, as_index=False).agg(aggregation)
    else:
        result = combined.drop_duplicates(subset=[selected_key]).copy()

    ordered_columns = [selected_key] + [
        column for column in combined.columns.tolist() if column != selected_key
    ]
    result = result[[column for column in ordered_columns if column in result.columns]]

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name
    result.to_excel(output_path, index=False)

    return ProcessResult(
        output_path=output_path,
        input_files=filenames,
        key_column=selected_key,
        numeric_columns=numeric_columns,
        text_columns=text_columns,
        input_rows=int(len(combined)),
        output_rows=int(len(result)),
    )
