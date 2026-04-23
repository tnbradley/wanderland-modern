"""Wanderland - Main entry point."""
from wanderland.core.game import GameState


def main() -> None:
    game = GameState()
    game.run()


if __name__ == "__main__":
    main()
