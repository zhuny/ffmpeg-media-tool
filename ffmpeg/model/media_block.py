from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List


@dataclass
class InputSource:
    file_path: Path
    key: str = ""


@dataclass
class MediaBlock:
    file_key: str
    start_point: Decimal
    end_point: Decimal
    speed: Decimal = Decimal(1)


@dataclass
class OutputSource:
    file_path: Path
    key: str = ""
    media_block_list: List[MediaBlock] = field(default_factory=list)
