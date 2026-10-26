"""Generic forbidden shapes; external token scanning also covers this policy source."""

import re

IDENTIFIERS = {
    "matrix-user": r"@[A-Za-z0-9._=+/-]+:[A-Za-z0-9.-]+",
    "matrix-event": r"\$[A-Za-z0-9_-]{20,}",
    "matrix-room": r"![A-Za-z0-9_-]{20,}(?::[A-Za-z0-9.-]+)?",
    "board-id": r"\b(?:TASK|STORY|BUG|EPIC)-\d{6}-[a-z0-9]{6}\b",
    "internal-name": r"\b[\w-]+-(?:dev|rev)\d+\b|\b[\w-]+_(?:dev|rev|orch)\d*\b",
    "local-path": r"/Users/|/home/[^\s/]+|~/|C:\\Users",
    "session-link": r"claude\.ai/code/session_|chatgpt\.com/codex/",
}
IDENTIFIERS = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in IDENTIFIERS.items()}
# This public skill invocation resembles an event token but is documented package metadata.
PUBLIC_INVOCATION = re.compile(r"\$swarma-platform-design-system(?![A-Za-z0-9_-])")
INVOCATION_FILES = {"agents/openai.yaml", "locales/metadata.json"}
RUSSIAN = re.compile(r"[А-Яа-яЁё]")
RUSSIAN_RULES = {
    "russian-guillemets": re.compile("[\u00ab\u00bb]"),
    "russian-dash": re.compile("[\u2012-\u2015]|(?<=\\S)[ \\t]+-[ \\t]+(?=\\S)"),
}

REPOSITORY = re.compile(r"github\.com/relux-works/([A-Za-z0-9_.-]+)", re.IGNORECASE)
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
