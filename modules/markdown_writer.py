from __future__ import annotations

from datetime import datetime
from pathlib import Path

from modules.excel_processor import ProcessResult


def write_process_markdown(result: ProcessResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "result.md"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    input_files = "\n".join(f"- {filename}" for filename in result.input_files)
    numeric_columns = ", ".join(result.numeric_columns) or "없음"
    text_columns = ", ".join(result.text_columns) or "없음"

    content = f"""# 엑셀 통합 처리 결과

## 생성 시간
- {generated_at}

## 입력 파일
{input_files}

## 처리 방식
- 기준 컬럼: {result.key_column}
- 숫자형 컬럼: 평균값 계산
- 문자형 컬럼: 첫 번째 값 유지

## 처리 컬럼
- 평균 처리 컬럼: {numeric_columns}
- 유지 처리 컬럼: {text_columns}

## 출력 파일
- {result.output_path.name}

## 처리 결과
- 총 입력 행 수: {result.input_rows}
- 출력 행 수: {result.output_rows}
"""
    markdown_path.write_text(content, encoding="utf-8")
    return markdown_path

