from enum import Enum


class BioAction:
    class Type(Enum):
        Message = 1
        React = 2
        Generate = 3
        Embed = 4
        Grammar = 41
        Vagina = 69

    class GenType(Enum):
        Response = 1
        TopTen = 2
        Subvert = 3

    def __init__(self, msg, channel, type=Type.Message, gen=GenType.Response):
        self._msg = msg
        self._channel = channel
        self._type = type
        self._gen = gen
