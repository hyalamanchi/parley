# 🎙️ Parley

**Parley** is a small, hackable **voice assistant** — you speak, it speaks back. The brain
is [Claude](https://www.anthropic.com/claude) by default, with an optional **free local
model** so you can run it with no API key at all. Your microphone and speakers are the
interface.

It's deliberately tiny and readable: one conversational loop, one brain wrapper, one
speech layer. A good starting point for anyone who wants to build voice interfaces on
top of an LLM.

```
You:  What's the weather like on Mars?
Parley:  Chilly and dramatic. Average around minus sixty Celsius, with dust storms that
         can wrap the whole planet. Want the summer-at-the-equator version instead?
You:  reset
Parley:  Okay, starting fresh. What's on your mind?
```

---

## Why Claude?

The default brain is the Claude API, on purpose — the details are in the write-up
**["Why I Built a Voice Bot with Claude (and not GPT-4)"](https://hyalamanchi.github.io/blog.html)**
on my site. The short version:

- **Instruction-following for *spoken* output.** A voice bot lives or dies on staying
  short and skipping markdown, lists, and code. Claude follows a "speak, don't format"
  system prompt tightly, which keeps the text-to-speech from reading "asterisk asterisk"
  out loud.
- **Natural, warm tone** that sounds right when read aloud.
- **A clean, well-typed Python SDK** that made the whole brain about 40 lines.

(Prefer to run it free and offline? Parley also speaks Llama via Ollama — see below.)

---

## How it works

```
   🎤 mic ──► Speech-to-Text ──► ┌──────────────────┐
                                 │  Claude · Ollama  │  (parley/brain.py)
   🔊 out ◄── Text-to-Speech ◄── └──────────────────┘
                                   keeps conversation
                                   history each turn
```

- **`parley/brain.py`** — a thin, stateful wrapper over the Claude Messages API, plus a
  `make_brain()` factory that can return the local Ollama brain instead.
- **`parley/ollama_brain.py`** — the free local backend (talks to Ollama over HTTP).
- **`parley/speech.py`** — speech-to-text (SpeechRecognition) and text-to-speech
  (pyttsx3). Both are optional; without them Parley runs in `--text` mode.
- **`parley/config.py`** — the model/provider choice and the spoken-assistant system prompt.
- **`parley/__main__.py`** — the conversational loop.

The Claude model defaults to **`claude-opus-5`**; set `ANTHROPIC_MODEL=claude-haiku-4-5`
for lower latency in a live voice loop.

---

## Quickstart

```bash
git clone https://github.com/hyalamanchi/parley.git
cd parley
pip install -r requirements.txt

# add your key (get one at https://console.anthropic.com/settings/keys)
cp .env.example .env        # then edit .env
#   ...or: export ANTHROPIC_API_KEY=sk-ant-...

# talk to it:
python -m parley

# no microphone? type instead:
python -m parley --text
```

> **macOS mic setup:** PyAudio needs PortAudio first — `brew install portaudio`, then
> `pip install PyAudio`. If you'd rather skip audio entirely, `--text` mode only needs
> the `anthropic` package.

### No API key? Run it free, locally, with Ollama

If you'd rather not use an API key, Parley also runs on a **free local model** via
[Ollama](https://ollama.com) — no key, works offline:

```bash
# 1. install Ollama (https://ollama.com) or: brew install ollama
# 2. pull a small model
ollama pull llama3.2
# 3. run Parley on the local brain
python -m parley --provider ollama --text
```

Claude stays the default and the showcased backend; Ollama is there for free local
testing and offline use. Pick a backend with `--provider claude|ollama`, or set
`VOICEBOT_PROVIDER` in your `.env`.

---

## Usage

| Command | What it does |
|---|---|
| `python -m parley` | Voice in, voice out |
| `python -m parley --text` | Type in, text out (no mic needed) |
| `python -m parley --no-speak` | Voice in, text out |
| `python -m parley --provider ollama --text` | Free local brain (no API key) |

In-conversation, say or type **"reset"** to start a new conversation, or **"quit"** to exit.

---

## Use it as a library

```python
from parley import Brain, make_brain

brain = Brain()                       # Claude; reads ANTHROPIC_API_KEY from the env
print(brain.reply("Give me a fun fact about octopuses."))
print(brain.reply("Do they have more than one?"))   # remembers context

local = make_brain("ollama")          # free local brain instead
print(local.reply("Say hi in three words."))
```

---

## Roadmap / ideas

- Swap Google STT for local Whisper (offline, private)
- Streaming replies so speech starts before the full answer is ready
- Tool use — let Parley check the weather or your calendar for real
- Wake-word ("Hey Parley") instead of push-to-talk

---

## License

MIT — see [LICENSE](LICENSE). Built by [Hemalatha Yalamanchi](https://hyalamanchi.github.io).
