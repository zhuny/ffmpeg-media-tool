from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List, Union


@dataclass
class InputSource:
    file_path: Path
    key: str = ""


@dataclass
class RotateFilter:
    degree: int  # it is degree


@dataclass
class TransposeFilter:
    rotate90: int


@dataclass
class CropFilter:
    x: int
    y: int
    width: int
    height: int


@dataclass
class MediaBlock:
    input_source: InputSource
    start_point: Decimal
    end_point: Decimal
    speed: Decimal = Decimal(1)
    filter_list: List[
        Union[RotateFilter, TransposeFilter, CropFilter]
    ] = field(default_factory=list)

    def f_rotate(self, degree):
        self.filter_list.append(RotateFilter(degree))

    def f_transpose(self, rotate90):
        self.filter_list.append(TransposeFilter(rotate90=rotate90))

    def f_crop(self, x, y, width, height):
        self.filter_list.append(CropFilter(x, y, width, height))


@dataclass
class OutputSource:
    file_path: Path
    key: str = ""
    media_block_list: List[MediaBlock] = field(default_factory=list)

    def is_exists(self):
        return self.file_path.exists()
