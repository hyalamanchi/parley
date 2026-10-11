"""Speech input (STT) and output (TTS).

Both are optional. If the audio libraries aren't installed, the bot still runs in
`--text` mode — so anyone can try it (including a recruiter clicking through) without
setting up a microphone. The heavy imports happen lazily inside the functions so
`import parley` never fails just because PyAudio isn't present.
"""
from __future__ import annotations


class SpeechUnavailable(RuntimeError):
    """Raised when an audio backend isn't installed, with an install hint."""


def speak(text: str) -> None:
    """Read text aloud with the offline pyttsx3 engine. Falls back silently if absent."""
    try:
        import pyttsx3
    except ImportError:
        return  # no TTS installed — caller still prints the text
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


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
    except (OSError, AttributeError) as exc:
        raise SpeechUnavailable(
            "No working microphone was found. Run with --text to type instead."
        ) from exc

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""  # heard nothing intelligible — caller re-prompts
    except sr.RequestError as exc:
        raise SpeechUnavailable(
            f"Speech-to-text service error: {exc}. Try again or use --text."
        ) from exc
