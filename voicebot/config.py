"""Configuration and the spoken-assistant system prompt."""
import os

# Default model. Override with the ANTHROPIC_MODEL env var.
# For lowest latency in a live voice loop you can set this to
# "claude-haiku-4-5"; the default favors answer quality.
DEFAULT_MODEL = "claude-opus-5"

# Kept deliberately small — spoken replies should be short, and a low
# cap keeps latency down. Override with VOICEBOT_MAX_TOKENS.
DEFAULT_MAX_TOKENS = 400

# The whole personality of the bot lives here. It's written for *speech*:
# no markdown, no lists, no code — because a TTS engine reads it out loud.
SYSTEM_PROMPT = (
    "You are a warm, concise voice assistant. Your words are read out loud by a "
    "text-to-speech engine, so speak the way a person speaks: short, natural "
    "sentences, usually one to three of them. "
    "Never use markdown, bullet points, headings, code blocks, or emoji — they "
    "sound wrong when spoken. Spell out symbols and units instead of using them. "
    "If a question needs a long answer, give the short version first and offer to "
    "go deeper. If you don't know something, say so briefly and honestly."
)


def get_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)


def get_max_tokens() -> int:
    try:
        return int(os.environ.get("VOICEBOT_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    except ValueError:
        return DEFAULT_MAX_TOKENS


def has_credentials() -> bool:
    """The Anthropic SDK also reads ANTHROPIC_AUTH_TOKEN / CLI profiles, but an
    API key is the common local-dev path — warn if none of the obvious ones exist."""
    return bool(
        os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    )
