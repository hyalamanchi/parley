"""The conversational brain(s).

Two interchangeable backends with the same interface (`.reply()`, `.reset()`,
`.messages`, `.model`):

- `ClaudeBrain` — the default, powered by the Claude API (needs an API key).
- `OllamaBrain` — a free local model via Ollama (see ollama_brain.py).

`make_brain()` picks one based on the provider. The Anthropic import is lazy, so
someone running only the Ollama backend doesn't need the `anthropic` package installed.
"""
from __future__ import annotations

from . import config


class ClaudeBrain:
    """Stateful wrapper over the Claude Messages API.

    The Messages API is stateless, so we keep the running transcript in
    `self.messages` and resend it every turn.
    """

    def __init__(
        self,
        client=None,
        model: str | None = None,
        system: str | None = None,
    ) -> None:
        import anthropic  # lazy: only needed for the Claude backend

        self._anthropic = anthropic
        # Zero-arg client resolves credentials from the environment
        # (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / an `ant auth login` profile).
        self.client = client or anthropic.Anthropic()
        self.model = model or config.get_model()
        self.system = system or config.SYSTEM_PROMPT
        self.messages: list[dict] = []

    def reply(self, user_text: str) -> str:
        """Send one user turn, append the reply to history, and return it as text."""
        anthropic = self._anthropic
        self.messages.append({"role": "user", "content": user_text})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=config.get_max_tokens(),
                system=self.system,
                messages=self.messages,
            )
        except anthropic.AuthenticationError:
            self.messages.pop()  # don't leave a dangling user turn in history
            return (
                "I couldn't authenticate with the Claude API. "
                "Check that your ANTHROPIC_API_KEY is set correctly."
            )
        except anthropic.RateLimitError:
            self.messages.pop()
            return "I'm being rate limited right now. Give it a moment and try again."
        except anthropic.APIStatusError as exc:
            self.messages.pop()
            if exc.status_code >= 500:
                return "The Claude API had a server error. Please try again in a bit."
            return f"Something went wrong talking to the API: {exc.message}"
        except anthropic.APIConnectionError:
            self.messages.pop()
            return "I can't reach the Claude API. Check your internet connection."

        # A voice bot only ever speaks text blocks.
        text = next((b.text for b in response.content if b.type == "text"), "")
        self.messages.append({"role": "assistant", "content": text})
        return text

    def reset(self) -> None:
        """Forget the conversation and start fresh."""
        self.messages.clear()


# Backward-compatible alias — ClaudeBrain is the original/default brain.
Brain = ClaudeBrain


def make_brain(
    provider: str | None = None,
    model: str | None = None,
    system: str | None = None,
):
    """Return the right brain for the chosen provider ('claude' or 'ollama')."""
    provider = (provider or config.get_provider()).lower()
    if provider == "ollama":
        from .ollama_brain import OllamaBrain

        return OllamaBrain(model=model, system=system)
    if provider == "claude":
        return ClaudeBrain(model=model, system=system)
    raise ValueError(f"Unknown provider: {provider!r} (use 'claude' or 'ollama')")
