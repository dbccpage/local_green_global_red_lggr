"""Replay the finite instance checked by proved_rows."""

import json

from proved_rows import replay_proved_rows


def main() -> None:
    print(json.dumps(replay_proved_rows(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
