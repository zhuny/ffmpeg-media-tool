from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class InputSource:
    filename: str
    key: str = ""


@dataclass
class MediaBlock:
    file_key: str
    start_point: Decimal
    end_point: Decimal
    speed: Decimal = Decimal(1)


@dataclass
class OutputSource:
    filename: str
    key: str
    media_block_list: List[MediaBlock]
