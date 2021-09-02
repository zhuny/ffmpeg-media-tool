from typing import Union

from pyffmpeg.model.filter_complex import Media, SourceOf, Filters


class LazyCreatedList(list):
    def __setitem__(self, key, value):
        while len(self) <= key:
            self.append(None)
        super().__setitem__(key, value)


class CommandBuilderVisitor:
    def __init__(self):
        self.index = 1
        self.char = "z"
        self.stream = []
        self.input_files = LazyCreatedList()
        self.last_key = None
        self.output_file = None

    def _get_key(self):
        key = f"[{self.char}{self.index}]"
        self.index += 1
        return key

    def visit(self, media: Union[Media, SourceOf]) -> str:
        if isinstance(media, Media):
            return self.visit_media(media)
        elif isinstance(media, SourceOf):
            return self.visit_source_of(media)
        else:
            pass

    def visit_media(self, media: Media) -> str:
        key_list = []
        for submedia in media.source_list:
            key_list.append(self.visit(submedia))
            if isinstance(submedia, Media):
                self.stream.append(";")

        self.stream.append("".join(key_list))
        for i, fi in enumerate(media.filters):
            self._concat_filter(fi)
            self.stream.append(",")
        if media.filters:
            self.stream.pop()
        key_list = [
            self._get_key() for i in range(media.count)
        ]
        self.stream.extend(key_list)
        self.last_key = key_list
        self.output_file = media.output_path
        return "".join(key_list)

    def _concat_filter(self, f: Filters):
        self.stream.append(f"{f.name}=")
        if f.args:
            self.stream.append(f.args)
        if f.kwargs:
            for k, v in f.kwargs.items():
                self.stream.append(f"{k}={v}")
                self.stream.append(":")
            if f.kwargs:
                self.stream.pop()

    def visit_source_of(self, source_of: SourceOf):
        self.input_files[source_of.source.index] = source_of.source.file_path
        char = source_of.kind.name[0]
        return f"[{source_of.source.index}:{char}]"

    def _build_command(self):
        yield "ffmpeg"
        for input_file in self.input_files:
            yield "-i"
            yield str(input_file)

        yield "-filter_complex"
        yield "".join(self.stream)

        for result in self.last_key:
            yield "-map"
            yield result

        yield '-b:v'
        yield '6715k'
        yield str(self.output_file)

    def end(self):
        return list(self._build_command())
