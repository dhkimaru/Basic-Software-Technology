from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from modules.excel_processor import merge_excel_average, preview_workbook
from modules.file_manager import (
    delete_file,
    ensure_storage,
    list_excel_files,
    save_uploaded_file,
)
from modules.llm_client import generate_response
from modules.markdown_writer import write_process_markdown
from modules.prompt_router import route_prompt


BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
OUTPUT_DIR = BASE_DIR / "storage" / "outputs"
LOG_DIR = BASE_DIR / "storage" / "logs"


def init_page() -> None:
    load_dotenv()
    ensure_storage([UPLOAD_DIR, OUTPUT_DIR, LOG_DIR])
    st.set_page_config(
        page_title="Basic Software Technology",
        page_icon="📊",
        layout="wide",
    )
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "엑셀 파일을 업로드한 뒤 '파일들을 합치고 동일 항목은 평균으로 계산해줘'처럼 입력해 주세요.",
            }
        ]


def render_sidebar() -> tuple[str, str]:
    st.sidebar.title("Basic Software Technology")
    provider = st.sidebar.selectbox("모델 제공자", ["none", "ollama", "openai", "gemini"])

    default_model = {
        "none": "",
        "ollama": "llama3.1",
        "openai": "gpt-4.1-mini",
        "gemini": "gemini-2.0-flash",
    }[provider]
    model = st.sidebar.text_input("모델명", value=default_model)

    st.sidebar.divider()
    st.sidebar.subheader("업로드 파일")
    files = list_excel_files(UPLOAD_DIR)
    if not files:
        st.sidebar.caption("업로드된 엑셀 파일이 없습니다.")
    for path in files:
        columns = st.sidebar.columns([0.72, 0.28])
        columns[0].caption(path.name)
        if columns[1].button("삭제", key=f"delete-{path.name}"):
            delete_file(UPLOAD_DIR, path.name)
            st.rerun()

    return provider, model


def render_uploader() -> None:
    uploaded_files = st.file_uploader(
        "엑셀 파일 업로드",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("업로드 파일 저장", type="primary"):
        saved = []
        for uploaded_file in uploaded_files:
            saved.append(save_uploaded_file(UPLOAD_DIR, uploaded_file).name)
        st.success(f"{len(saved)}개 파일을 저장했습니다: {', '.join(saved)}")
        st.rerun()


def render_file_preview() -> None:
    files = list_excel_files(UPLOAD_DIR)
    if not files:
        st.info("먼저 xlsx 또는 xls 파일을 업로드해 주세요.")
        return

    st.subheader("파일 미리보기")
    selected = st.selectbox("미리보기 파일", files, format_func=lambda path: path.name)
    try:
        preview = preview_workbook(selected)
        st.caption(
            f"시트: {preview.sheet_name} | 행 수: {preview.row_count} | 컬럼: {', '.join(preview.columns)}"
        )
        st.dataframe(pd.read_excel(selected, sheet_name=0, nrows=20), use_container_width=True)
    except Exception as exc:
        st.error(f"미리보기 실패: {exc}")


def show_downloads() -> None:
    xlsx_path = OUTPUT_DIR / "merged_average.xlsx"
    md_path = OUTPUT_DIR / "result.md"
    if not xlsx_path.exists() and not md_path.exists():
        return

    st.subheader("결과 다운로드")
    columns = st.columns(2)
    if xlsx_path.exists():
        columns[0].download_button(
            "결과 엑셀 다운로드",
            data=xlsx_path.read_bytes(),
            file_name=xlsx_path.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if md_path.exists():
        columns[1].download_button(
            "결과 MD 다운로드",
            data=md_path.read_text(encoding="utf-8"),
            file_name=md_path.name,
            mime="text/markdown",
        )


def run_merge_from_prompt() -> str:
    files = list_excel_files(UPLOAD_DIR)
    result = merge_excel_average(files, OUTPUT_DIR)
    md_path = write_process_markdown(result, OUTPUT_DIR)
    return (
        f"처리 완료: {len(result.input_files)}개 파일, 입력 {result.input_rows}행을 "
        f"{result.output_rows}행으로 통합했습니다. 기준 컬럼은 '{result.key_column}'입니다. "
        f"결과 파일: {result.output_path.name}, {md_path.name}"
    )


def handle_prompt(prompt: str, provider: str, model: str) -> str:
    routed = route_prompt(prompt)
    if routed.name == "merge_excel_average":
        return run_merge_from_prompt()
    if routed.name == "list_files":
        files = list_excel_files(UPLOAD_DIR)
        if not files:
            return "현재 업로드된 엑셀 파일이 없습니다."
        return "업로드된 파일:\n" + "\n".join(f"- {path.name}" for path in files)
    if routed.name == "help":
        return (
            "가능한 작업: 엑셀 파일 업로드, 목록 확인, 삭제, 여러 엑셀 파일 병합, "
            "동일 항목 기준 숫자 컬럼 평균 계산, 결과 xlsx/md 저장 및 다운로드."
        )

    if provider != "none":
        response = generate_response(provider, model, prompt)
        return response.text

    return (
        "아직 실행할 수 있는 엑셀 작업으로 판단하지 못했습니다. "
        "예: '업로드된 엑셀 파일들을 합치고 동일 항목은 평균으로 계산해줘'"
    )


def render_chat(provider: str, model: str) -> None:
    st.subheader("프롬프트")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("엑셀 처리 요청을 입력하세요")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        answer = handle_prompt(prompt, provider, model)
    except Exception as exc:
        answer = f"처리 실패: {exc}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)


def main() -> None:
    init_page()
    provider, model = render_sidebar()

    st.title("Basic Software Technology")
    st.caption("Streamlit 기반 파일 관리, 엑셀 병합/평균 처리, LLM 프롬프트 보조 MVP")

    left, right = st.columns([0.48, 0.52])
    with left:
        render_uploader()
        render_file_preview()
        show_downloads()
    with right:
        render_chat(provider, model)


if __name__ == "__main__":
    main()
