import dataclasses


@dataclasses.dataclass
class Data:
    title: str
    url: str
    exchange: str
    releaseDate: str
    timeParsing: str
    catalogName: str or None
    text: str or None = None
