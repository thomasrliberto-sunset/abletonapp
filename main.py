"""Simple command-line entry point for the scaffold app."""

from argparse import ArgumentParser, Namespace


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Run the simple Python scaffold app.")
    parser.add_argument(
        "--name",
        default="world",
        help="Name to greet.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"Hello, {args.name}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
