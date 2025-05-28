from pathlib import PurePath, Path
from typing import TypeAlias, Literal, LiteralString, Any
from collections.abc import Callable, Iterable, Sequence

StrPath: TypeAlias = str | Path

# class Success(Exception):
#     def __init__(self, msg: LiteralString = ...):
#         super().__init__(msg)
#         self.msg = msg
