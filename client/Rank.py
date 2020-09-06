
RANK_MAP = {
    0: 'Uncalibrated',
    1: 'Herald',
    2: 'Guardian',
    3: 'Crusader',
    4: 'Archon',
    5: 'Legend',
    6: 'Ancient',
    7: 'Divine',
    8: 'Immortal'
}


class Rank:
    """
    Represents a rank in DotA
    """

    def __init__(self, rankNbr):
        self._rankNbr = rankNbr
        self._medal, self._level = self._parseRankNbr(rankNbr)

    def _parseRankNbr(self, rankNbr):
        medal = 0
        level = 0

        if rankNbr:
            medal = int(str(rankNbr)[0])
            level = int(str(rankNbr)[1])

        return medal, level

    @property
    def medal(self) -> str:
        return RANK_MAP[self._medal]

    @property
    def level(self) -> int:
        return self._level

    def convertBack(self):
        """
        Converts the medal back to the number representation
        :return: String like "55" for Legend 5
        """
        return int('{}{}'.format(self._medal, self._level))

    def toStr(self):
        if self._medal == 0:    # Uncalibrated
            return '{}'.format(self.medal)

        else:
            return '{} {}'.format(self.medal, self.level)

    def __repr__(self):
        if self._medal == 0:    # Uncalibrated
            return 'Rank<{}>'.format(self.medal)

        else:
            return 'Rank<{} {}>'.format(self.medal, self.level)
