from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List, Union


@dataclass
class InputSource:
    file_path: Path
    key: str = ""


@dataclass
class Rotate:
    degree: int  # it is degree


@dataclass
class Transpose:
    rotate90: int


@dataclass
class MediaBlock:
    input_source: InputSource
    start_point: Decimal
    end_point: Decimal
    speed: Decimal = Decimal(1)
    filter_list: List[Union[Rotate, Transpose]] = field(default_factory=list)


@dataclass
class OutputSource:
    file_path: Path
    key: str = ""
    media_block_list: List[MediaBlock] = field(default_factory=list)

    def is_exists(self):
        return self.file_path.exists()
