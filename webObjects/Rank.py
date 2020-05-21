

class Rank:
    """
    Represents a rank in DotA
    """

    def __init__(self, rankNbr):
        self._rankNbr = rankNbr
        self._medal, self._level = self._parseRankNbr(rankNbr)

    def _parseRankNbr(self, rankNbr):
        rank_map = {
            '1': 'Herald',
            '2': 'Guardian',
            '3': 'Crusader',
            '4': 'Archon',
            '5': 'Legend',
            '6': 'Ancient',
            '7': 'Divine',
            '8': 'Immortal'
        }

        if rankNbr:
            medal = rank_map[str(rankNbr)[0]]
            level = int(str(rankNbr)[1])
            return medal, level

        else:
            return 'Uncalibrated', 0


    @property
    def medal(self):
        return self._medal

    @property
    def level(self):
        return self._level


    def __repr__(self):
        if self.medal == 'Uncalibrated':
            return 'Rank<{}>'.format(self.medal)

        else:
            return 'Rank<{} {}>'.format(self.medal, self.level)
