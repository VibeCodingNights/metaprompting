"""Pydantic schemas for taste extraction.

The TasteDirective is the unit of taste in this repo. Every challenge reads
or writes these. The schema is strict on purpose — loose schemas let models
write "make it clean" and call it a directive.

See TASTE_FORMAT.md for field semantics and worked examples.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TasteDirective(BaseModel):
    """One axis of taste, extracted from a session or audited from a rules file."""

    dimension: str = Field(
        ...,
        description=(
            "The axis this directive legislates — one word or short phrase. "
            "Examples: register, palette, motion, typography, voice, density, rhythm."
        ),
    )
    keep: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description=(
            "Patterns to maintain — observed in outputs that were kept. "
            "Specific imperatives, not vague praise like 'good spacing'."
        ),
    )
    avoid: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description=(
            "Patterns to reject — observed in outputs that were discarded. "
            "The shape of the wrong answer."
        ),
    )
    reference: str = Field(
        ...,
        min_length=10,
        description=(
            "ONE evocative sentence. Not advice. A feeling. "
            "'a page that breathes' — not 'use muted colors'. "
            "This is the test of whether taste was captured or collapsed."
        ),
    )


class TasteProfile(BaseModel):
    """A set of directives extracted from one session or one rules file."""

    source: str = Field(..., description="Where these came from — session title or file path.")
    directives: list[TasteDirective] = Field(
        ...,
        min_length=1,
        max_length=8,
        description="3–5 directives is the sweet spot. More than 8 is noise.",
    )


class AuditFinding(BaseModel):
    """Output of auditing an existing rules file."""

    config_rule_count: int = Field(..., description="How many config rules exist today.")
    taste_directive_count: int = Field(..., description="How many taste directives exist today.")
    implied_taste: list[TasteDirective] = Field(
        ...,
        description=(
            "Taste that is implied by the tone or phrasing of the config rules "
            "but never stated as a directive."
        ),
    )
    summary: str = Field(
        ...,
        description="One paragraph describing the gap between stated config and implied taste.",
    )


class JudgeVerdict(BaseModel):
    """Output of the taste judge in Challenge 3."""

    preferred: str = Field(..., description="Either 'A' or 'B' — which output better matches the taste profile.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0 — how clear the preference is.")
    reasoning: str = Field(
        ...,
        description=(
            "Why. Cite specific elements of the chosen output and specific "
            "clauses of the taste profile. No hand-waving."
        ),
    )
    ineffective_directives: list[str] = Field(
        default_factory=list,
        description=(
            "Directives from the profile that the judge could not find honored "
            "in either output. Evidence that the directive is not landing."
        ),
    )
