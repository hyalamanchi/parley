"""Entry point: `python -m voicebot`.

Runs a conversational loop. Voice mode by default; `--text` types instead of
speaking (handy when you have no mic, or for a quick demo).
"""
from __future__ import annotations

import argparse
import sys

from . import config
from .brain import Brain
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


def run(text_mode: bool, voice_out: bool) -> int:
    _load_dotenv()

    if not config.has_credentials():
        print(
            "⚠️  No ANTHROPIC_API_KEY found.\n"
            "   Set it first:  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "   (or copy .env.example to .env and fill it in)",
            file=sys.stderr,
        )
        return 1

    brain = Brain()
    print(f"🤖 Claude Voice Bot — model: {brain.model}")
    print("   Say or type something. Say 'quit' to exit, 'reset' to start over.\n")

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
    args = parser.parse_args()
    # In text mode, default to not speaking unless the user still wants audio out.
    voice_out = not args.no_speak and not args.text
    sys.exit(run(text_mode=args.text, voice_out=voice_out))


if __name__ == "__main__":
    main()
