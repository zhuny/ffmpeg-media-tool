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


@dataclass
class SourceOf:
    source: InputMedia
    kind: KindEnum


@dataclass
class Filters:
    name: str
    args: Optional[str] = None
    kwargs: Dict[str, str] = field(default_factory=dict)


@dataclass
class Media:
    source_list: List[Union['Media', SourceOf]]
    filters: List[Filters]
    count: int = 1
    output_path: Path = None
