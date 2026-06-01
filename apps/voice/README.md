# Arizen Voice

> `@arizen/voice` — Wake-word detection, speech-to-text, and voice command routing.

Runs as a background service, always listening for the wake word. Routes voice commands to ArizenAssistant and ArizenAgent. All processing is local — no audio leaves the device.

## Responsibilities

- Wake-word detection (Porcupine / Picovoice, local)
- Speech-to-text transcription (Whisper.cpp, local GGUF)
- Text-to-speech synthesis (Kokoro / Piper, local)
- Command routing to Assistant and Agent
- Voice status overlay (listening indicator)

## Tech Stack

| Layer | Technology |
|---|---|
| Wake word | Porcupine (local, MIT-compatible model) |
| STT | Whisper.cpp (GGUF, runs on CPU+GPU) |
| TTS | Kokoro / Piper (local neural TTS) |
| Runtime | Node.js native module + Electron tray |
| IPC | `@arizen/core` event bus |

## Development

```bash
pnpm --filter @arizen/voice dev
pnpm --filter @arizen/voice test
pnpm --filter @arizen/voice build
```

## Privacy

Arizen Voice processes all audio locally. The microphone stream is never transmitted to any server. Wake-word detection runs on a small, dedicated CPU thread. STT only activates post-wake-word. See [`/SECURITY.md`](../../SECURITY.md).

## Module Owner

See [`/MAINTAINERS.md`](../../MAINTAINERS.md)
