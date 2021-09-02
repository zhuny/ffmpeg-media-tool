from decimal import Decimal
from pathlib import Path

from pyffmpeg.model.media_block import InputSource, OutputSource, MediaBlock


class RandomKeyDict(dict):
    def __init__(self):
        super().__init__()
        self._current_key_array = ["A", "A"]

    def _current_key(self):
        return "".join(self._current_key_array)

    def _next_key(self):
        up = True
        for i, char in enumerate(self._current_key_array):
            if not up:
                break
            elif char == "Z":
                self._current_key_array[i] = "A"
            else:
                self._current_key_array[i] = chr(ord(char) + 1)
                up = False
        if up:
            self._current_key_array.append("A")

    def add_value(self, v):
        key = self._current_key()
        self[key] = v
        self._next_key()
        return key


class MediaController:
    def __init__(self):
        self.input_source = RandomKeyDict()
        self.output_source = RandomKeyDict()

    def add_input_source(self, file_path: Path):
        input_source = InputSource(file_path=file_path)
        key = self.input_source.add_value(input_source)
        input_source.key = key

    def add_output_source(self, file_path: Path):
        output_source = OutputSource(file_path=file_path)
        key = self.output_source.add_value(output_source)
        output_source.key = key

    def add_output_block(self, input_key, output_key, start, end, speed):
        input_source = self.input_source[input_key]
        output_source = self.output_source[output_key]
        block = MediaBlock(
            file_key=input_source.key,
            start_point=Decimal(start),
            end_point=Decimal(end),
            speed=Decimal(speed)
        )
        output_source.media_block_list.append(block)

    def convert(self):
        pass
