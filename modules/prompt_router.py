from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoutedTask:
    name: str
    reason: str


def route_prompt(prompt: str) -> RoutedTask:
    text = prompt.lower()
    merge_words = ["합쳐", "통합", "병합", "merge", "combine"]
    average_words = ["평균", "mean", "average"]
    list_words = ["목록", "리스트", "파일", "list"]
    help_words = ["도움", "help", "사용법"]

    wants_merge = any(word in text for word in merge_words)
    wants_average = any(word in text for word in average_words)

    if wants_merge and wants_average:
        return RoutedTask(
            name="merge_excel_average",
            reason="프롬프트에서 병합과 평균 계산 의도를 찾았습니다.",
        )
    if wants_merge:
        return RoutedTask(
            name="merge_excel_average",
            reason="현재 MVP에서는 병합 요청을 동일 항목 평균 병합으로 처리합니다.",
        )
    if any(word in text for word in list_words):
        return RoutedTask(name="list_files", reason="파일 목록 확인 요청으로 판단했습니다.")
    if any(word in text for word in help_words):
        return RoutedTask(name="help", reason="사용법 안내 요청으로 판단했습니다.")

    return RoutedTask(
        name="chat_only",
        reason="정해진 엑셀 작업 키워드를 찾지 못했습니다.",
    )

