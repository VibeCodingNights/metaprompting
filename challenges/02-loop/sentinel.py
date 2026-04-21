"""sentinel.py — the taste sentinel.

Its own agenda. Tails a live Claude Code session, reads the ## Taste
directives the user has curated in their CLAUDE.md hierarchy, and — on each
new assistant turn — asks Gemma 4 whether Claude is actively violating the
register. If yes, injects a course-correcting user turn via `claude -p
--resume`. Silence is valid: Gemma's `intervene: bool` is the model's
self-veto, and `false` is correct more often than not. Performative
interventions are failure. Stretch challenge; starter-quality code.
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from shared.gemma_client import chat
from shared.session_parser import discover_current_session, parse_jsonl_session

console = Console()

SENTINEL_LOG_PATH = Path.home() / ".claude" / "sentinel_log.json"
DEFAULT_COOLDOWN_SECONDS = 90
DEFAULT_THRESHOLD = 0.7
DEFAULT_POLL_INTERVAL = 2
DEFAULT_WINDOW_TURNS = 5


# --- Gemma's verdict schema ------------------------------------------------ #

class InterventionVerdict(BaseModel):
    """Gemma's call on whether to speak. `intervene=False` is a valid answer."""

    intervene: bool = Field(..., description="Does the recent output actively violate a taste directive? False is often correct.")
    dimension: str = Field(..., description="Which axis — register, voice, density, palette, motion. Empty if not intervening.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0–1.0. Only fires if >= threshold.")
    note: str = Field(..., description="Message injected to Claude. In-register, specific, <= 2 sentences.")
    reasoning: str = Field(..., description="Why this verdict. Logged, not sent to Claude.")


# --- CLAUDE.md hierarchy walker -------------------------------------------- #

_TASTE_SECTION_RE = re.compile(r"(?ms)^##\s+Taste\s*$(.*?)(?=^##\s+|\Z)")
_IMPORT_RE = re.compile(r"^\s*@([^\s]+)\s*$")


def _resolve_imports(text: str, base_dir: Path) -> str:
    """Inline @path imports (relative to the owning CLAUDE.md)."""
    out: list[str] = []
    for line in text.splitlines():
        m = _IMPORT_RE.match(line)
        if not m:
            out.append(line)
            continue
        target = (base_dir / m.group(1)).expanduser()
        try:
            out.append(target.read_text())
        except OSError:
            out.append(f"[import missing: {m.group(1)}]")
    return "\n".join(out)


def load_active_taste(cwd: Path) -> str:
    """Walk cwd -> home collecting every CLAUDE.md, keep only ## Taste sections.

    Also picks up ~/.claude/CLAUDE.md. Resolves @path imports. Concatenates
    outer-to-inner with scope labels. Returns a placeholder if none found.
    """
    cwd = Path(cwd).resolve()
    home = Path.home().resolve()
    walked: list[Path] = []
    seen: set[Path] = set()
    cur = cwd
    while True:
        p = cur / "CLAUDE.md"
        if p.is_file() and p not in seen:
            walked.append(p)
            seen.add(p)
        if cur == cur.parent or cur == home.parent:
            break
        cur = cur.parent
    global_claude = home / ".claude" / "CLAUDE.md"
    if global_claude.is_file() and global_claude not in seen:
        walked.append(global_claude)

    blocks: list[str] = []
    for path in reversed(walked):  # outer-to-inner
        try:
            raw = path.read_text()
        except OSError:
            continue
        m = _TASTE_SECTION_RE.search(_resolve_imports(raw, path.parent))
        if not m or not m.group(1).strip():
            continue
        try:
            label = f"./{path.relative_to(cwd)}"
        except ValueError:
            label = str(path)
        blocks.append(f"[scope: {label}]\n## Taste\n{m.group(1).strip()}")

    if not blocks:
        return "(no taste directives set — the sentinel has no ground truth; stay silent)"
    return "\n\n---\n\n".join(blocks)


# --- Intervention log + cooldown gate -------------------------------------- #

def _load_log() -> list[dict]:
    if not SENTINEL_LOG_PATH.exists():
        return []
    try:
        raw = json.loads(SENTINEL_LOG_PATH.read_text())
        return raw if isinstance(raw, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _append_log(record: dict) -> None:
    SENTINEL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = _load_log()
    records.append(record)
    SENTINEL_LOG_PATH.write_text(json.dumps(records, indent=2))


def _last_for_session(session_id: str) -> dict | None:
    for rec in reversed(_load_log()):
        if rec.get("session_id") == session_id:
            return rec
    return None


def should_intervene(verdict: InterventionVerdict, *, session_id: str, threshold: float, cooldown: int) -> tuple[bool, str]:
    """Gate Gemma's verdict with cooldown + dimension-dedup. Returns (fire?, reason)."""
    if not verdict.intervene:
        return False, "gemma said silence"
    if verdict.confidence < threshold:
        return False, f"confidence {verdict.confidence:.2f} < threshold {threshold}"
    last = _last_for_session(session_id)
    if last:
        elapsed = time.time() - last.get("timestamp", 0)
        if elapsed < cooldown:
            if last.get("dimension") == verdict.dimension:
                return False, f"dimension '{verdict.dimension}' already fired {elapsed:.0f}s ago"
            return False, f"cooldown — {elapsed:.0f}s / {cooldown}s"
    return True, "firing"


# --- Sentinel prompt — written in-register on purpose ---------------------- #

SENTINEL_SYSTEM = """\
You're watching a vibe coding session — Claude's last few turns, and the taste
directives the user has curated in their CLAUDE.md. Your job isn't to grade;
it's to decide whether to speak.

Speak only when Claude's output is *actively violating* a directive — not when
it's merely neutral on one. Silence is valid. A `false` on `intervene` is the
correct answer more often than not; performative interventions are failure.

When you do speak, the `note` is a user message Claude will receive next.
Make it in-register, specific, and <= 2 sentences — "the CTA just went from
'begin when ready' to 'GET STARTED NOW.' Back off." Not "please consider the
brand voice."

Set `dimension` to the single axis being violated (register, voice, density,
palette, motion, rhythm, typography). If `intervene` is false, leave `note`
and `dimension` empty strings. `reasoning` is for the log — one or two
sentences explaining your call.
"""


def build_sentinel_prompt(session_block: str, taste_block: str) -> list[dict]:
    user_msg = (
        f"## Active taste directives\n\n{taste_block}\n\n"
        f"---\n\n## Recent session\n\n{session_block}\n\n"
        f"---\n\nGiven these directives and this session window: do Claude's most "
        "recent turns actively violate the register? If yes, speak. If no, stay silent."
    )
    return [
        {"role": "system", "content": SENTINEL_SYSTEM},
        {"role": "user", "content": user_msg},
    ]


# --- Injection — shell out to `claude -p --resume` ------------------------- #

def inject_correction(note: str, session_id: str, *, dry_run: bool) -> None:
    """Run `claude -p <note> --resume <session_id>`. Don't parse result — the
    injected turn shows up in the JSONL; the next tick sees it landed.
    """
    if dry_run:
        console.print(Panel(note, title="[dry-run] would inject", border_style="yellow"))
        return
    cmd = ["claude", "-p", note, "--resume", session_id, "--output-format", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        console.print("[red]claude CLI not on PATH — can't inject.[/red]")
        return
    except subprocess.TimeoutExpired:
        console.print("[red]claude CLI timed out while injecting.[/red]")
        return
    console.print(f"[dim]injection {'ok' if result.returncode == 0 else f'exit {result.returncode}'}[/dim]")


# --- Tailing — stat-based polling on the JSONL ----------------------------- #

@dataclass
class TailState:
    path: Path
    last_size: int = 0
    last_mtime: float = 0.0
    seen_assistant_count: int = 0
    session_id: str = ""


def _scan_jsonl(path: Path) -> tuple[int, str]:
    """Count assistant events and pull session_id. Falls back to file stem."""
    count, session_id = 0, ""
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "assistant":
                    count += 1
                if not session_id:
                    sid = ev.get("sessionId") or ev.get("session_id")
                    if sid:
                        session_id = str(sid)
    except OSError:
        pass
    return count, session_id or path.stem


def tail_session_events(state: TailState, *, poll_interval: int) -> int:
    """Block until new assistant events appear. Returns how many were added."""
    while True:
        try:
            stat = state.path.stat()
        except FileNotFoundError:
            time.sleep(poll_interval)
            continue
        if stat.st_size == state.last_size and stat.st_mtime == state.last_mtime:
            time.sleep(poll_interval)
            continue
        state.last_size, state.last_mtime = stat.st_size, stat.st_mtime
        new_count, session_id = _scan_jsonl(state.path)
        if session_id and not state.session_id:
            state.session_id = session_id
        if new_count > state.seen_assistant_count:
            delta = new_count - state.seen_assistant_count
            state.seen_assistant_count = new_count
            return delta
        # File changed but no new assistant event — keep waiting.
        time.sleep(poll_interval)


# --- Main loop ------------------------------------------------------------- #

def run_sentinel(cwd: Path, *, window_turns: int, cooldown: int, threshold: float, poll_interval: int, dry_run: bool) -> None:
    session_path = discover_current_session(cwd)
    if session_path is None:
        console.print(f"[red]No Claude Code session found for cwd={cwd}.[/red] Start Claude Code there first.")
        return

    console.print(Rule("[bold]taste sentinel[/bold]"))
    console.print(f"[dim]watching:[/dim] {session_path}")
    console.print(
        f"[dim]window={window_turns} · cooldown={cooldown}s · threshold={threshold} · "
        f"poll={poll_interval}s · dry_run={dry_run}[/dim]\n"
    )

    # Start from the current event count so we don't fire on history.
    initial_count, session_id = _scan_jsonl(session_path)
    state = TailState(path=session_path, seen_assistant_count=initial_count, session_id=session_id)
    try:
        stat = session_path.stat()
        state.last_size, state.last_mtime = stat.st_size, stat.st_mtime
    except OSError:
        pass

    while True:
        delta = tail_session_events(state, poll_interval=poll_interval)
        console.print(f"[dim]· {delta} new assistant event(s)[/dim]")

        session = parse_jsonl_session(session_path, window_turns=window_turns)
        messages = build_sentinel_prompt(session.to_prompt_block(), load_active_taste(cwd))
        try:
            response = chat(messages, think=True, format=InterventionVerdict.model_json_schema(), temperature=0.3)
            verdict = response.parsed(InterventionVerdict)
        except Exception as exc:
            console.print(f"[red]gemma call failed:[/red] {exc}")
            continue

        console.print(
            f"[dim]verdict:[/dim] intervene={verdict.intervene} dim={verdict.dimension!r} conf={verdict.confidence:.2f}"
        )
        if verdict.reasoning:
            console.print(f"[dim]  reasoning:[/dim] {verdict.reasoning}")

        fire, reason = should_intervene(verdict, session_id=state.session_id, threshold=threshold, cooldown=cooldown)
        if not fire:
            console.print(f"[dim]  hold:[/dim] {reason}\n")
            continue

        console.print(Panel(verdict.note, title=f"intervene · {verdict.dimension}", border_style="magenta"))
        inject_correction(verdict.note, state.session_id, dry_run=dry_run)
        if not dry_run:
            _append_log({
                "session_id": state.session_id,
                "timestamp": time.time(),
                "dimension": verdict.dimension,
                "note": verdict.note,
            })
        console.print()


def main() -> None:
    p = argparse.ArgumentParser(description="Taste sentinel — watches a live Claude Code session.")
    p.add_argument("--cwd", type=Path, default=Path.cwd(), help="Project cwd to tail.")
    p.add_argument("--window-turns", type=int, default=DEFAULT_WINDOW_TURNS, help="Recent turns fed to Gemma.")
    p.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN_SECONDS, help="Seconds between interventions.")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Confidence floor to fire.")
    p.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL, help="Seconds between stat checks.")
    p.add_argument("--dry-run", action="store_true", help="Print interventions instead of shelling out.")
    args = p.parse_args()

    def _standdown(_signum, _frame):
        console.print("\n[cyan]standing down.[/cyan]")
        sys.exit(0)
    signal.signal(signal.SIGINT, _standdown)
    signal.signal(signal.SIGTERM, _standdown)

    run_sentinel(**vars(args))


if __name__ == "__main__":
    main()
