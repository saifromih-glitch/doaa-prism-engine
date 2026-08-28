"""Deterministic parser for Doaa Structured Command Language v1.

This module only parses explicit command syntax. It does not infer intent,
call models, access the network, execute commands, or mutate any state.
"""
from __future__ import annotations

import re
import shlex
from typing import Any

CONTRACT = "doaa.command.v1"
_MAX_COMMAND_LENGTH = 2048
_MAX_VALUE_LENGTH = 512
_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_HEAD_RE = re.compile(r"^@([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)$")
_PAIR_RE = re.compile(r"^([a-z][a-z0-9_]*)=(.*)$")
_TEMPLATES = {
    "marketing.campaign": frozenset({"goal", "audience", "channel", "language"}),
    "sales.pipeline": frozenset({"goal", "stage", "language"}),
    "software.task": frozenset({"goal", "language"}),
    "science.explain": frozenset({"topic", "level", "language"}),
}
_LIBRARIES = frozenset({"science", "industry", "software", "business", "marketing", "sales", "education", "language", "general"})


def parse_command(command: Any) -> dict[str, Any]:
    """Parse one explicit command and return a stable, non-executable result."""
    if not isinstance(command, str):
        return _blocked("command_must_be_string")
    if not command or len(command) > _MAX_COMMAND_LENGTH:
        return _blocked("command_length_invalid")
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        return _blocked("quote_syntax_invalid")
    if not parts:
        return _blocked("command_empty")
    head = _HEAD_RE.fullmatch(parts[0])
    if head is None:
        return _blocked("command_head_invalid")
    library, template = head.groups()
    capability = f"{library}.{template}"
    if library not in _LIBRARIES:
        return _proposal(command, capability, "library_not_supported")
    required = _TEMPLATES.get(capability)
    if required is None:
        return _proposal(command, capability, "template_not_registered")
    slots: dict[str, str] = {}
    for raw in parts[1:]:
        match = _PAIR_RE.fullmatch(raw)
        if match is None:
            return _blocked("slot_syntax_invalid")
        key, value = match.groups()
        if not _KEY_RE.fullmatch(key):
            return _blocked("slot_key_invalid")
        if key in slots:
            return _blocked("duplicate_slot")
        if key not in required:
            return _blocked("unknown_slot")
        value = _unquote(value)
        if not value or len(value) > _MAX_VALUE_LENGTH or any(symbol in value for symbol in (";", "|", "&", "`", "$", "<", ">")):
            return _blocked("slot_value_invalid")
        slots[key] = value
    missing = sorted(required - slots.keys())
    if missing:
        return _blocked("missing_required_slots", missing_slots=missing)
    return {
        "status": "command_parsed",
        "contract": CONTRACT,
        "command": command,
        "capability": capability,
        "library": library,
        "template": template,
        "slots": slots,
        "execution_authority": "none",
        "automatic_execution": False,
        "model_call": False,
        "network_access": False,
    }


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {"status": "command_blocked", "contract": CONTRACT, "reason": reason, **extra, "execution_authority": "none", "automatic_execution": False}


def _proposal(command: str, capability: str, reason: str) -> dict[str, Any]:
    return {"status": "governed_capability_request", "contract": CONTRACT, "submitted_command": command, "requested_capability": capability, "reason": reason, "required_review": ["contract", "threat_model", "tests", "human_approval"], "execution_authority": "none", "automatic_execution": False}
