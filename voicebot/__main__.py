"""Entry point: `python -m voicebot`.

Runs a conversational loop. Voice mode by default; `--text` types instead of
speaking (handy when you have no mic, or for a quick demo).
"""
from __future__ import annotations

import argparse
import sys

from . import config
from .brain import make_brain
from .speech import SpeechUnavailable, listen, speak

QUIT_WORDS = {"quit", "exit", "goodbye", "bye", "stop"}
RESET_WORDS = {"reset", "start over", "new conversation"}


def _load_dotenv() -> None:
    """Load a local .env if python-dotenv is installed (optional convenience)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def run(text_mode: bool, voice_out: bool, provider: str, model: str | None) -> int:
    _load_dotenv()

    provider = (provider or config.get_provider()).lower()

    # The Claude backend needs a key; the local Ollama backend does not.
    if provider == "claude" and not config.has_credentials():
        print(
            "⚠️  No ANTHROPIC_API_KEY found.\n"
            "   Set it first:  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "   (or copy .env.example to .env and fill it in)\n"
            "   No key? Run a free local model instead:  --provider ollama",
            file=sys.stderr,
        )
        return 1

    try:
        brain = make_brain(provider=provider, model=model)
    except ValueError as exc:
        print(f"⚠️  {exc}", file=sys.stderr)
        return 1

    print(f"🤖 Claude Voice Bot — provider: {provider}, model: {brain.model}")
    print("   Say or type something. Say 'quit' to exit, 'reset' to start over.\n")

    if provider == "ollama":
        greeting = f"Hi! I'm your local voice assistant ({brain.model}). What can I help you with?"
    else:
        greeting = "Hi! I'm your Claude voice assistant. What can I help you with?"
    print(f"Bot: {greeting}")
    if voice_out:
        speak(greeting)

    while True:
        # ---- get the user's turn ----
        try:
            if text_mode:
                user_text = input("You: ").strip()
            else:
                try:
                    user_text = listen().strip()
                except SpeechUnavailable as exc:
                    print(f"\n{exc}\n")
                    return 1
                if not user_text:
                    print("(didn't catch that — try again)")
                    continue
                print(f"You: {user_text}")
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            return 0

        if not user_text:
            continue

        lowered = user_text.lower().strip(".!? ")
        if lowered in QUIT_WORDS:
            farewell = "Talk to you later!"
            print(f"Bot: {farewell}")
            if voice_out:
                speak(farewell)
            return 0
        if lowered in RESET_WORDS:
            brain.reset()
            print("Bot: Okay, starting fresh. What's on your mind?")
            continue

        # ---- Claude's turn ----
        reply = brain.reply(user_text)
        print(f"Bot: {reply}")
        if voice_out:
            speak(reply)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="voicebot", description="A voice assistant powered by Claude."
    )
    parser.add_argument(
        "--text", action="store_true",
        help="Type instead of speaking (no microphone needed).",
    )
    parser.add_argument(
        "--no-speak", action="store_true",
        help="Don't read replies aloud (text only).",
    )
    parser.add_argument(
        "--provider", choices=["claude", "ollama"], default=None,
        help="Which brain to use: 'claude' (default, needs a key) or 'ollama' (free, local).",
    )
    parser.add_argument(
        "--model", default=None,
        help="Override the model id (e.g. claude-haiku-4-5, or an Ollama model like llama3.2).",
    )
    args = parser.parse_args()
    # In text mode, default to not speaking unless the user still wants audio out.
    voice_out = not args.no_speak and not args.text
    sys.exit(run(
        text_mode=args.text, voice_out=voice_out,
        provider=args.provider, model=args.model,
    ))


if __name__ == "__main__":
    main()
