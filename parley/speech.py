"""Speech input (STT) and output (TTS).

Both are optional. If the audio libraries aren't installed, the bot still runs in
`--text` mode — so anyone can try it (including a recruiter clicking through) without
setting up a microphone. The heavy imports happen lazily inside the functions so
`import parley` never fails just because PyAudio isn't present.
"""
from __future__ import annotations

import os

# Female voices to prefer, best-sounding first. macOS "Enhanced"/"Premium" voices
# (download them in System Settings > Accessibility > Spoken Content > System Voice)
# sound far nicer than the default compact ones — if installed, they're picked here.
_FEMALE_VOICES = [
    "ava", "allison", "samantha", "susan", "zoe", "serena",
    "victoria", "karen", "moira", "tessa", "fiona", "female",
]

_engine = None  # cached so we don't rebuild it (and re-pick the voice) every turn


class SpeechUnavailable(RuntimeError):
    """Raised when an audio backend isn't installed, with an install hint."""


def _configure_voice(engine) -> None:
    """Pick a female voice and a pleasant speaking rate. Overridable via env:
    VOICEBOT_VOICE (name/id substring) and VOICEBOT_RATE (words per minute)."""
    try:
        engine.setProperty("rate", int(os.environ.get("VOICEBOT_RATE", "178")))
    except Exception:
        pass

    voices = engine.getProperty("voices") or []
    want = os.environ.get("VOICEBOT_VOICE", "").lower().strip()
    order = [want] if want else _FEMALE_VOICES

    def blob(v):
        return ((getattr(v, "id", "") or "") + " " + (getattr(v, "name", "") or "")).lower()

    # Pass 1: prefer a higher-quality "enhanced"/"premium" female voice.
    # Pass 2: fall back to any matching female voice (e.g. the built-in compact one).
    for quality_only in (True, False):
        for needle in order:
            if not needle:
                continue
            for v in voices:
                b = blob(v)
                if quality_only and "premium" not in b and "enhanced" not in b:
                    continue
                if needle in b:
                    engine.setProperty("voice", v.id)
                    return


def speak(text: str) -> None:
    """Read text aloud with the offline pyttsx3 engine. Falls back silently if absent."""
    global _engine
    try:
        import pyttsx3
    except ImportError:
        return  # no TTS installed — caller still prints the text
    if _engine is None:
        _engine = pyttsx3.init()
        _configure_voice(_engine)
    _engine.say(text)
    _engine.runAndWait()


def listen(timeout: float = 8.0, phrase_time_limit: float = 15.0) -> str:
    """Capture one utterance from the microphone and transcribe it to text.

    Uses SpeechRecognition with Google's free recognizer (needs internet, no key).
    Raises SpeechUnavailable if the audio stack isn't installed.
    """
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise SpeechUnavailable(
            "Speech input needs SpeechRecognition + PyAudio. "
            "Install them, or run with --text.\n"
            "  pip install SpeechRecognition PyAudio"
        ) from exc

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("🎙️  Listening…")
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
    except sr.WaitTimeoutError:
        # No speech detected in time — not an error; let the caller re-prompt.
        # If this keeps happening, the mic usually lacks permission (macOS:
        # System Settings > Privacy & Security > Microphone > enable your terminal).
        return ""
    except (OSError, AttributeError) as exc:
        raise SpeechUnavailable(
            "No working microphone was found. Check that your terminal has "
            "microphone permission, or run with --text to type instead."
        ) from exc

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""  # heard nothing intelligible — caller re-prompts
    except sr.RequestError as exc:
        raise SpeechUnavailable(
            f"Speech-to-text service error: {exc}. Try again or use --text."
        ) from exc
    except (FileNotFoundError, OSError) as exc:
        # Google STT converts audio to FLAC via a 'flac' binary. If it's missing
        # (common on macOS), the conversion subprocess fails here.
        raise SpeechUnavailable(
            "Speech-to-text needs the 'flac' encoder, which isn't installed.\n"
            "  Install it:  brew install flac\n"
            "Then run voice mode again — or use --text in the meantime."
        ) from exc
