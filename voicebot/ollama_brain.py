"""A free, local brain backed by Ollama (https://ollama.com).

Same interface as ClaudeBrain (`.reply()`, `.reset()`, `.messages`, `.model`), so the
rest of the app doesn't care which brain it's talking to. Talks to a local Ollama
server over its REST API using only the standard library — no extra pip package, no
API key, works offline once a model is pulled.

Setup:
    1. Install Ollama:   https://ollama.com  (or `brew install ollama`)
    2. Pull a model:     ollama pull llama3.2
    3. Run the bot:      python -m voicebot --provider ollama --text
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from . import config


class OllamaBrain:
    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        host: str | None = None,
    ) -> None:
        self.model = model or config.get_ollama_model()
        self.system = system or config.SYSTEM_PROMPT
        self.host = (host or config.get_ollama_host()).rstrip("/")
        self.messages: list[dict] = []

    def reply(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": self.system}] + self.messages,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            self.messages.pop()
            detail = ""
            try:
                detail = json.loads(exc.read()).get("error", "")
            except Exception:
                pass
            if exc.code == 404 or "not found" in detail.lower():
                return (
                    f"The model '{self.model}' isn't pulled yet. "
                    f"Run:  ollama pull {self.model}"
                )
            return f"Ollama returned an error ({exc.code}): {detail or exc.reason}"
        except urllib.error.URLError:
            self.messages.pop()
            return (
                f"I can't reach Ollama at {self.host}. "
                "Install it from ollama.com, start it with 'ollama serve', then pull a "
                f"model:  ollama pull {self.model}"
            )

        text = (body.get("message") or {}).get("content", "").strip()
        if not text:
            self.messages.pop()
            return "Ollama returned an empty response. Try a different model."

        self.messages.append({"role": "assistant", "content": text})
        return text

    def reset(self) -> None:
        self.messages.clear()
