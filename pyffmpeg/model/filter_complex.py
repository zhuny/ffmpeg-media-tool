from dataclasses import dataclass
from enum import Enum
from typing import Union, List, Dict


@dataclass
class InputMedia:
    pass


class KindEnum(Enum):
    video = "VIDEO"
    audio = "AUDIO"


class SourceOf:
    source: InputMedia
    kind: KindEnum


class Filters:
    name: str
    kwargs: Dict[str, str]


class Media:
    source: List[Union['Media', SourceOf]]
    filters: List[Filters]
