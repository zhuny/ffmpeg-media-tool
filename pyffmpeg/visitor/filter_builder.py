from pyffmpeg.model.filter_complex import Media, Filters, SourceOf, \
    InputMedia, KindEnum
from pyffmpeg.model.media_block import OutputSource, InputSource, MediaBlock, \
    RotateFilter, TransposeFilter


class FilterBuilderVisitor:
    def __init__(self):
        self.key_count = {}
        self.result = None

    def visit(self, output):
        self.result = self.visit_output_source(output)

    def end(self):
        return self.result

    def visit_output_source(self, output: OutputSource):
        source_list = []
        for block in output.media_block_list:
            source_list.extend(self.visit_media_block(block))

        return Media(
            source_list=source_list,
            filters=[
                Filters(
                    "concat",
                    kwargs={
                        "n": f"{len(output.media_block_list)}",
                        "v": "1",
                        "a": "1"
                    }
                )
            ],
            count=2,
            output_path=output.file_path
        )

    def visit_media_block(self, block: MediaBlock):
        input_media = self.visit_input_source(block.input_source)
        yield Media(
            source_list=[
                SourceOf(source=input_media, kind=KindEnum.video)
            ],
            filters=list(self._trim_with_speed(block, KindEnum.video))
        )
        yield Media(
            source_list=[
                SourceOf(source=input_media, kind=KindEnum.audio)
            ],
            filters=list(self._trim_with_speed(block, KindEnum.audio))
        )

    def _trim_with_speed(self, block: MediaBlock, kind_enum: KindEnum):
        # 자르는 부분
        yield Filters(
            self._filter_name('trim', kind_enum),
            kwargs={
                "start": str(block.start_point),
                "end": str(block.end_point)
            }
        )
        yield Filters(
            self._filter_name("setpts", kind_enum),
            args="PTS-STARTPTS"
        )

        # 스피드 조절하기
        inv = 1 / block.speed
        if block.speed == 1:
            pass
        elif kind_enum == KindEnum.video:
            yield Filters("setpts", args=f"PTS*{inv}")
            yield Filters(
                "minterpolate",
                kwargs={
                    "mi_mode": "mci",
                    "mc_mode": "aobmc",
                    "vsbmc": "1"
                }
            )
        elif kind_enum == KindEnum.audio:
            yield Filters("atempo", args=f"{block.speed}")

        # 회전
        if kind_enum == KindEnum.video:
            for fi in block.filter_list:
                if isinstance(fi, RotateFilter):
                    yield Filters("rotate", args=f"{fi.degree}*PI/180")
                elif isinstance(fi, TransposeFilter):
                    yield Filters("transpose", kwargs={'dir': f"{fi.rotate90}"})
                else:
                    print("Unknown Filter :", fi)

    def _filter_name(self, name, kind_enum: KindEnum):
        if kind_enum == KindEnum.video:
            return name
        elif kind_enum == KindEnum.audio:
            return f"a{name}"

    def visit_input_source(self, input_source: InputSource):
        key = input_source.key
        if key not in self.key_count:
            self.key_count[key] = len(self.key_count)

        return InputMedia(
            index=self.key_count[key],
            file_path=input_source.file_path
        )
