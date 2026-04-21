"""Shared utilities for the metaprompting challenges.

Import from here — don't modify unless you're extending. The challenge code
should stay readable; put plumbing here.
"""

from .rules_io import (
    RulesFile,
    amend_scoped,
    append_taste,
    extract_taste_section,
    read_rules,
    render_directive,
    suggest_scope,
)
from .taste_schema import (
    AuditFinding,
    JudgeVerdict,
    TasteDirective,
    TasteProfile,
)

__all__ = [
    "AuditFinding",
    "JudgeVerdict",
    "RulesFile",
    "TasteDirective",
    "TasteProfile",
    "amend_scoped",
    "append_taste",
    "extract_taste_section",
    "read_rules",
    "render_directive",
    "suggest_scope",
]
