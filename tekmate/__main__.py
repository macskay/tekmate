# -*- encoding: utf-8 -*-
from tekmate.game import PyGameInitializer, TekmateFactory


def main():
    initializer = PyGameInitializer({"display_width": 1280, "display_height": 800})
    game_factory = TekmateFactory(initializer)
    game = game_factory.create()
    game.enter_mainloop()

if __name__ == "__main__":
    main()
