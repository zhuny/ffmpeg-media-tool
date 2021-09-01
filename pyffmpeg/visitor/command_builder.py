from typing import Union

from pyffmpeg.model.filter_complex import Media, SourceOf, Filters


class CommandBuilderVisitor:
    def __init__(self):
        self.index = 1
        self.char = "z"
        self.stream = []

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
            self.stream.append(";")

        self.stream.append("".join(key_list))
        for i, fi in enumerate(media.filters):
            self._concat_filter(fi)
            self.stream.append(",")
        if media.filters:
            self.stream.pop()
        key = self._get_key()
        self.stream.append(key)
        return key

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
        char = source_of.kind.name[0]
        return f"[{source_of.source.index}:{char}]"
