from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import List


@dataclass
class InputSource:
    filename: Path
    key: str = ""


@dataclass
class MediaBlock:
    file_key: str
    start_point: Decimal
    end_point: Decimal
    speed: Decimal = Decimal(1)


@dataclass
class OutputSource:
    filename: Path
    key: str
    media_block_list: List[MediaBlock]
