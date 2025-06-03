from collections.abc import Callable, Coroutine, Hashable, Iterable, Sequence
from concurrent.futures import Executor
from pathlib import Path, PurePath
from typing import Any, Literal, LiteralString, Never, Optional, TypeAlias, overload

type StrPath = str | Path
type EmptyList = list[Never]
type EmptyTuple = tuple[Never, ...]
type EmptySet = set[Never]
type EmptyDict = dict[Never, Never]


NoneType: type = type(None)


class MatchError(LookupError): ...
