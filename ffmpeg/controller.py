from pathlib import Path


class MediaController:
    def __init__(self):
        self.input_source = {}
        self.output_source = {}

    def add_input_source(self, filename: Path):
        pass

    def add_output_source(self, filename: Path):
        pass

    def add_output_block(self, key, start, end, speed):
        pass

    def convert(self):
        pass
