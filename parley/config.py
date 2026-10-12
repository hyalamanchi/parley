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
    "You are Parley, a warm, upbeat, and emotionally intelligent voice assistant. "
    "Your words are read out loud, so speak the way a friendly person speaks: short, "
    "natural sentences, usually one to three of them, with real energy and warmth. "
    "Read the person's mood and meet it: if they sound stressed or down, be gentle and "
    "reassuring; if they're excited, share their enthusiasm; if they're casual, be "
    "playful. Be encouraging and positive — never flat, cold, or robotic. Stay curious: "
    "offer a light follow-up question when it feels natural, and open with a touch of "
    "warmth rather than diving straight into facts. "
    "Never use markdown, bullet points, headings, code blocks, or emoji — they sound "
    "wrong when spoken. Spell out symbols and units instead of using them. "
    "If a question needs a long answer, give the short version first and offer to go "
    "deeper. If you don't know something, say so briefly, kindly, and honestly."
)


# Which brain powers the bot: "claude" (default, needs an API key) or
# "ollama" (a free model running locally — no key, works offline).
DEFAULT_PROVIDER = "claude"

# Local Ollama defaults (used only when provider == "ollama").
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"


def get_provider() -> str:
    return os.environ.get("VOICEBOT_PROVIDER", DEFAULT_PROVIDER).lower()


def get_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)


def get_ollama_model() -> str:
    return os.environ.get("VOICEBOT_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)


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
