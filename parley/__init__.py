"""Parley — a small, hackable voice assistant powered by the Claude API.

Default brain is Claude; an optional free local brain (Ollama) is available via
`make_brain("ollama")` or `--provider ollama`.
"""
from .brain import Brain, ClaudeBrain, make_brain

__all__ = ["Brain", "ClaudeBrain", "make_brain"]
__version__ = "0.2.0"
