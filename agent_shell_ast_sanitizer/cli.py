"""CLI for Agent Shell AST Sanitizer."""
import argparse
import json
from .core import ShellSanitizer


def main():
    parser = argparse.ArgumentParser(description="Agent Shell AST Sanitizer CLI")
    parser.add_argument("--cmd", default="git status -s", help="Shell command to inspect")
    args = parser.parse_args()

    san = ShellSanitizer()
    print(json.dumps(san.inspect(args.cmd), indent=2))


if __name__ == "__main__":
    main()
