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
    speed: Decimal = Decimal(1)

    def __repr__(self):
        return f"{self.start_point}-{self.end_point}(X{self.speed})"

    def contains(self, speed_change):
        return (
            self.file_path == speed_change.file_path and
            self.start_point <= speed_change.changed_at < self.end_point
        )

    def split(self, speed_change: 'SpeedChange'):
        if self.start_point == speed_change.changed_at:
            yield Interval(
                start_point=self.start_point,
                end_point=self.end_point,
                file_path=self.file_path,
                speed=speed_change.speed
            )
        else:
            yield Interval(
                start_point=self.start_point,
                end_point=speed_change.changed_at,
                file_path=self.file_path,
                speed=self.speed
            )
            yield Interval(
                start_point=speed_change.changed_at,
                end_point=self.end_point,
                file_path=self.file_path,
                speed=speed_change.speed
            )


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

    def _split_interval(self, speed_change):
        for interval in self.check_point:
            if interval.contains(speed_change):
                yield from interval.split(speed_change)
            else:
                yield interval

    def set_speed(self, speed_change_list: List['SpeedChange']):
        for speed_change in speed_change_list:
            self.check_point = list(self._split_interval(speed_change))


@dataclass
class SpeedChange:
    changed_at: Decimal
    speed: Decimal
    file_path: Path


class TeamInfo(collections.defaultdict):
    def __init__(self):
        super().__init__(OneLevel)


class TimeContainer:
    def __init__(self):
        self.pattern_interval = re.compile(r"([a-zA-Z]+)(\d+)cp(\d)([ab])")
        self.pattern_speed = re.compile(r"x(\d)")
        self.map_info = collections.defaultdict(TeamInfo)
        self.controller = MediaController()
        self.speed_info = []

    def _find_tick(self, tick_code):
        for tick_com in tick_code.split('|'):
            if g := self.pattern_interval.fullmatch(tick_com):
                return g
            else:
                print(__file__, tick_com)

    def set_time(self, tick_code, time_info, file_path):
        for tick_com in tick_code.split('|'):
            if g := self.pattern_interval.fullmatch(tick_com):
                team_name, counter, check_point, opening = g.groups()
                counter = int(counter)
                check_point = int(check_point)

                self.map_info[team_name][counter].set_time(
                    check_point,
                    opening, time_info,
                    file_path
                )
            elif g := self.pattern_speed.fullmatch(tick_com):
                speed = Decimal(g.group(1))
                self.speed_info.append(
                    SpeedChange(time_info, speed, file_path)
                )

    def show(self):
        for name, info in self.map_info.items():
            print(name)
            for index, level in sorted(info.items()):
                print(
                    f"    {name}{index} : {len(level.check_point)}",
                    level.check_point
                )

    def adjust_speed(self):
        for team, team_level in self.map_info.items():
            for index, level in team_level.items():
                level.set_speed(self.speed_info)

    def add_output(self, output_name, level_code_list):
        print(output_name, level_code_list)
        out_key = self.controller.add_output_source(output_name)

        pattern = re.compile(r"([a-z]+)(\d+)")
        for level_code in level_code_list:
            if g := pattern.fullmatch(level_code):
                team, counter = g.groups()
                counter = int(counter)
                print(level_code)
                for block in self.map_info[team][counter].check_point:
                    in_key = self.controller.add_input_source(block.file_path)
                    self.controller.add_output_block(
                        in_key, out_key,
                        block.start_point, block.end_point
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


def show_group(input_folder: Path, output_folder: Path):
    line_match = re.compile(r'\d+=(.+)')
    time_group = TimeContainer()

    suffix_map = {
        f.stem: f
        for f in input_folder.glob('*')
        if f.suffix != '.gbm'
    }

    for f in input_folder.glob('*.gbm'):
        if f.stem not in suffix_map:
            continue

        matched_ts = suffix_map[f.stem]
        for line in f.open():
            g = line_match.match(line)
            if g is not None:
                info = g.group(1).split()
                time_group.set_time(info[1], Decimal(info[0]), matched_ts)

    time_group.adjust_speed()

    with (input_folder / 'output.txt').open() as f:
        for output, levels in group_n(f, 2, 1):
            time_group.add_output(output_folder / output, levels.split(','))


def main():
    show_group(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == '__main__':
    main()
