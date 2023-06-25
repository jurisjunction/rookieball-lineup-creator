class Player:
    def __init__(self, name):
        self._name = name
        self._positions = {}

    def add_position(self, position, inning):
        self._positions[inning] = position

    @property
    def name(self):
        return self._name

    @property
    def positions(self):
        return self._positions


