# ADR-003: Named Pipes + gRPC for IPC

**Date:** 2025-06  
**Status:** Accepted  
**Owner:** Platform team

## Decision

IPC uses Windows Named Pipes for low-latency real-time messaging (streaming tokens, events)
and gRPC (localhost:50051) for structured request-response calls.

## Named Pipes (MessagePack encoded)

```
\\.\pipe\arizen-control    →  Daemon lifecycle commands
\\.\pipe\arizen-agents     →  Agent message bus (high throughput)
\\.\pipe\arizen-events     →  Pub-sub event stream (fire and forget)
\\.\pipe\arizen-nexus      →  Command Nexus ↔ Daemon (streaming tokens)
```

Use when: streaming output, real-time events, high-frequency messages.

## gRPC (tonic, localhost:50051)

Use when: structured request-response, strong typing, one-off queries.

```protobuf
service Daemon     { rpc GetStatus, ListAgents, SendTask, StreamEvents }
service AgentMesh  { rpc DelegateTask, GetAgentStatus, SetAgentConfig }
service Knowledge  { rpc Query, Ingest, ListNamespaces }
```

## Why not Unix sockets / WebSocket?

- Unix sockets are not available on Windows without WSL.
- WebSocket introduces HTTP overhead and browser-security framing.
- Named pipes are the Windows-native equivalent of Unix domain sockets.

## Message encoding: MessagePack (not JSON)

Hot paths (token streaming, event bus) use MessagePack for ~6x smaller payload vs JSON.
Structured gRPC calls use Protobuf (already binary).
