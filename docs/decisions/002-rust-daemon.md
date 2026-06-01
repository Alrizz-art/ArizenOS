# ADR-002: Rust Daemon as the Process Spine

**Date:** 2025-06  
**Status:** Accepted  
**Owner:** Platform team

## Decision

The ArizenOS process manager, IPC router, and all background services run in a single Rust binary (the daemon).

## Rationale

1. **Named pipe performance.** Windows named pipes in Rust (via `tokio`) have sub-millisecond latency. Python's asyncio named pipe support is fragile on Windows.
2. **Memory footprint.** The daemon idles at < 30 MB RSS. A Python equivalent would be > 150 MB with asyncio + dependencies.
3. **Process supervision.** Rust gives us fine-grained control over `spawn`, `kill`, and `waitpid` on Windows child processes without interpreter overhead.
4. **Windows API access.** `windows-rs` provides direct bindings to RegisterHotKey, clipboard API, and WMI — no ctypes marshaling.

## Consequences

- All Tier 0 and Tier 1 code is Rust. Platform team owns it.
- Python intelligence layer communicates with the daemon exclusively via named pipes or gRPC.
- Tauri (also Rust) shares the same workspace, enabling future shared Cargo crate reuse.
