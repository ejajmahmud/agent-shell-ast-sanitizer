"""Core POSIX shell command tokenizer and injection sanitizer."""
import shlex
from typing import Any, Dict, List, Set


class ShellSanitizer:
    """Inspects agent shell strings for command chaining, subshells, and disallowed binaries."""

    DANGEROUS_OPERATORS = {";", "&&", "||", "|", ">", ">>", "<", "&"}

    def __init__(self, allowed_bins: Set[str] = None):
        self.allowed_bins = set(allowed_bins or {"git", "python", "pytest", "ls", "cat", "rg"})

    def inspect(self, command: str) -> Dict[str, Any]:
        reasons: List[str] = []
        if "$(" in command or "`" in command:
            reasons.append("subshell_substitution_detected")

        try:
            lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError as exc:
            return {"allowed": False, "reasons": [f"lex_error:{exc}"], "tokens": []}

        if not tokens:
            return {"allowed": False, "reasons": ["empty_command"], "tokens": []}

        for tok in tokens:
            if tok in self.DANGEROUS_OPERATORS:
                reasons.append(f"disallowed_operator:{tok}")

        binary = tokens[0].split("/")[-1]
        if binary not in self.allowed_bins:
            reasons.append(f"disallowed_binary:{binary}")

        if binary == "rm" and any(t in ("-rf", "-fr", "/") for t in tokens[1:]):
            reasons.append("destructive_rm_flags")

        return {
            "allowed": len(reasons) == 0,
            "binary": binary,
            "tokens": tokens,
            "reasons": sorted(set(reasons)),
        }
