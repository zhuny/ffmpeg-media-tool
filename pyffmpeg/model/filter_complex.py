from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Union, List, Dict, Optional


@dataclass
class InputMedia:
    index: int
    file_path: Path


class KindEnum(Enum):
    video = "VIDEO"
    audio = "AUDIO"


class SourceOf:
    source: InputMedia
    kind: KindEnum


class Filters:
    name: str
    args: Optional[str]
    kwargs: Dict[str, str] = field(default_factory=dict)


class Media:
    source_list: List[Union['Media', SourceOf]]
    filters: List[Filters]
