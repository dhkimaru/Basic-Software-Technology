from __future__ import annotations

import os
from dataclasses import dataclass


SYSTEM_PROMPT = """당신은 엑셀 파일 처리 보조 AI입니다.
사용자에게 간결하게 답하고, 임의의 코드를 실행하라고 지시하지 마세요.
실제 파일 처리는 앱에 등록된 안전한 함수만 수행합니다."""


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    text: str


def generate_response(provider: str, model: str, prompt: str) -> LLMResponse:
    provider = provider.lower()
    if provider == "ollama":
        return _ollama_response(model, prompt)
    if provider == "openai":
        return _openai_response(model, prompt)
    if provider == "gemini":
        return _gemini_response(model, prompt)
    return LLMResponse(provider="none", text="AI 모델이 선택되지 않았습니다.")


def _ollama_response(model: str, prompt: str) -> LLMResponse:
    try:
        import ollama

        client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        response = client.chat(
            model=model or "llama3.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return LLMResponse(provider="ollama", text=response["message"]["content"])
    except Exception as exc:
        return LLMResponse(provider="ollama", text=f"Ollama 호출 실패: {exc}")


def _openai_response(model: str, prompt: str) -> LLMResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return LLMResponse(provider="openai", text="OPENAI_API_KEY가 설정되지 않았습니다.")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model or "gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return LLMResponse(provider="openai", text=response.output_text)
    except Exception as exc:
        return LLMResponse(provider="openai", text=f"OpenAI 호출 실패: {exc}")


def _gemini_response(model: str, prompt: str) -> LLMResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return LLMResponse(provider="gemini", text="GEMINI_API_KEY가 설정되지 않았습니다.")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model or "gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\n\n사용자 요청:\n{prompt}",
        )
        return LLMResponse(provider="gemini", text=response.text or "")
    except Exception as exc:
        return LLMResponse(provider="gemini", text=f"Gemini 호출 실패: {exc}")

