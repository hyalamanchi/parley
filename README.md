# 🎙️ Claude Voice Bot

A small, hackable **voice assistant powered by [Claude](https://www.anthropic.com/claude)**.
Speak to it, and it speaks back — Claude is the brain, your microphone and speakers are
the interface.

It's deliberately tiny and readable: one conversational loop, one API wrapper, one
speech layer. A good starting point for anyone who wants to build voice interfaces on
top of an LLM.

```
You:  What's the weather like on Mars?
Bot:  Chilly and dramatic. Average around minus sixty Celsius, with dust storms that
      can wrap the whole planet. Want the summer-at-the-equator version instead?
You:  reset
Bot:  Okay, starting fresh. What's on your mind?
```

---

## Why Claude?

I built this on the Claude API on purpose — the details are in the write-up
**["Why I Built a Voice Bot with Claude (and not GPT-4)"](https://hyalamanchi.github.io/blog.html)**
on my site. The short version:

- **Instruction-following for *spoken* output.** A voice bot lives or dies on staying
  short and skipping markdown, lists, and code. Claude follows a "speak, don't format"
  system prompt tightly, which keeps the text-to-speech from reading "asterisk asterisk"
  out loud.
- **Natural, warm tone** that sounds right when read aloud.
- **A clean, well-typed Python SDK** that made the whole brain about 40 lines.

---

## How it works

```
   🎤 mic ──► Speech-to-Text ──► ┌───────────────┐
                                 │  Claude API   │  (voicebot/brain.py)
   🔊 out ◄── Text-to-Speech ◄── └───────────────┘
                                  keeps conversation
                                  history each turn
```

- **`voicebot/brain.py`** — a thin, stateful wrapper over the Claude Messages API. The API
  is stateless, so it keeps the transcript and resends it each turn.
- **`voicebot/speech.py`** — speech-to-text (SpeechRecognition) and text-to-speech
  (pyttsx3). Both are optional; without them the bot runs in `--text` mode.
- **`voicebot/config.py`** — the model choice and the spoken-assistant system prompt.
- **`voicebot/__main__.py`** — the conversational loop.

The model defaults to **`claude-opus-5`**; set `ANTHROPIC_MODEL=claude-haiku-4-5` for
lower latency in a live voice loop.

---

## Quickstart

```bash
git clone https://github.com/hyalamanchi/claude-voice-bot.git
cd claude-voice-bot
pip install -r requirements.txt

# add your key (get one at https://console.anthropic.com/settings/keys)
cp .env.example .env        # then edit .env
#   ...or: export ANTHROPIC_API_KEY=sk-ant-...

# talk to it:
python -m voicebot

# no microphone? type instead:
python -m voicebot --text
```

> **macOS mic setup:** PyAudio needs PortAudio first — `brew install portaudio`, then
> `pip install PyAudio`. If you'd rather skip audio entirely, `--text` mode only needs
> the `anthropic` package.

---

## Usage

| Command | What it does |
|---|---|
| `python -m voicebot` | Voice in, voice out |
| `python -m voicebot --text` | Type in, text out (no mic needed) |
| `python -m voicebot --no-speak` | Voice in, text out |

In-conversation, say or type **"reset"** to start a new conversation, or **"quit"** to exit.

---

## Use it as a library

```python
from voicebot import Brain

brain = Brain()                       # reads ANTHROPIC_API_KEY from the env
print(brain.reply("Give me a fun fact about octopuses."))
print(brain.reply("Do they have more than one?"))   # remembers context
```

---

## Roadmap / ideas

- Swap Google STT for local Whisper (offline, private)
- Streaming replies so speech starts before the full answer is ready
- Tool use — let the bot check the weather or your calendar for real
- Wake-word ("Hey Claude") instead of push-to-talk

---

## License

MIT — see [LICENSE](LICENSE). Built by [Hemalatha Yalamanchi](https://hyalamanchi.github.io).
