import collections
import re
import sys
from dataclasses import field, dataclass
from decimal import Decimal
from pathlib import Path
from typing import List

from pyffmpeg.controller import MediaController


@dataclass
class Interval:
    start_point: Decimal = None
    end_point: Decimal = None
    file_path: Path = None

    def __repr__(self):
        return f"{self.start_point}-{self.end_point}"


@dataclass
class OneLevel:
    check_point: List[Interval] = field(default_factory=list)

    def set_time(self,
                 check_point: int, opening: str, time_info: Decimal,
                 file_path: Path):
        while len(self.check_point) <= check_point:
            self.check_point.append(Interval())

        interval = self.check_point[check_point]
        if opening == 'a':
            interval.start_point = time_info
        else:
            interval.end_point = time_info
        interval.file_path = file_path


class TeamInfo(collections.defaultdict):
    def __init__(self):
        super().__init__(OneLevel)


class TimeContainer:
    def __init__(self):
        self.pattern = re.compile(r"([a-z]+)(\d+)cp(\d)([ab])")
        self.map_info = collections.defaultdict(TeamInfo)
        self.controller = MediaController()

    def _find_tick(self, tick_code):
        for tick_com in tick_code.split('|'):
            if g := self.pattern.fullmatch(tick_com):
                return g

    def set_time(self, tick_code, time_info, file_path):
        g = self.pattern.fullmatch(tick_code)
        if g is None:
            return

        team_name, counter, check_point, opening = g.groups()
        counter = int(counter)
        check_point = int(check_point)

        self.map_info[team_name][counter].set_time(
            check_point,
            opening, time_info,
            file_path
        )

    def show(self):
        for name, info in self.map_info.items():
            print(name)
            for index, level in sorted(info.items()):
                print(
                    f"    {name}{index} : {len(level.check_point)}",
                    level.check_point
                )


def group_n(iterable, n, m):
    before = []
    skip_it = n
    next_skip = m
    is_skip = False

    for e in iterable:
        before.append(e.strip())
        if len(before) == skip_it:
            if not is_skip:
                yield tuple(before)
            before = []
            skip_it, next_skip = next_skip, skip_it
            is_skip = not is_skip


def show_group(input_folder: Path):
    line_match = re.compile(r'\d+=(.+)')
    time_group = TimeContainer()
    for f in input_folder.glob('*.gbm'):
        for line in f.open():
            g = line_match.match(line)
            if g is not None:
                info = g.group(1).split()
                time_group.set_time(info[1], Decimal(info[0]), f)

    time_group.show()

    with (input_folder / 'output.txt').open() as f:
        for output, levels in group_n(f, 2, 1):
            print(output, levels)


def main():
    show_group(Path(sys.argv[1]))


if __name__ == '__main__':
    main()
