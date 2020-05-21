
class Avatar:

    def __init__(self, small, medium, full):
        self._small = small
        self._medium = medium
        self._full = full

    @property
    def small(self):
        return self._small

    @property
    def medium(self):
        return self._medium

    @property
    def full(self):
        return self._full

    def __repr__(self) -> str:
        return 'Avatars<>'


