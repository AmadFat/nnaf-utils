from .pytype import *


def _remove_symlink_or_file(
    path: Path,
    error_callback: Callable[..., Any] = None,
) -> None | Exception:
    try:
        if not (path.is_symlink() or path.is_file()):
            raise ValueError(f"Cannot solve object {path}: not a symlink or file.")
        path.unlink(missing_ok=False)
    except Exception as e:
        if error_callback:
            error_callback(e)
        return e


def _remove_dir(
    path: Path,
    strict: bool = False,
    error_callback: Callable[..., Any] = None,
) -> list[Exception]:
    # If strict, return exception immediately when occurs.
    # If not, collect exceptions and return at last.

    collected_excs = []

    try:
        for obj in path.iterdir():
            issymlink = obj.is_symlink()
            isfile = obj.is_file()
            isdir = obj.is_dir()
            match [issymlink, isfile, isdir]:
                case [True, _, _] | [False, True, _]:
                    exc = _remove_symlink_or_file(obj, error_callback=error_callback)
                    excs = [exc] if exc is not None else []

                case [False, _, True]:
                    excs = _remove_dir(obj, strict=strict, error_callback=error_callback)

                case _:
                    symlink_info = "a symlink" if issymlink else "not a symlink"
                    file_info = "a file" if isfile else "not a file"
                    dir_info = "a directory" if isdir else "not a directory"
                    exc = MatchError(f"Cannot solve object {obj}: {symlink_info}, {file_info}, and {dir_info}.")
                    if error_callback:
                        error_callback(exc)
                    excs = [exc]

            match [len(excs) > 0, strict]:
                case [True, True]:
                    return excs
                case [True, False]:
                    collected_excs.extend(excs)

        path.rmdir()

    except Exception as e:
        if error_callback:
            error_callback(e)
        if strict:
            return [e]
        else:
            collected_excs.append(e)

    return collected_excs


def refresh_obj(
    obj: StrPath,
    strict: bool = True,
    return_exc: bool = False,
    success_callback: Callable[..., Any] = None,
    error_callback: Callable[..., Any] = None,
) -> None | list[Exception]:
    collected_excs = []

    try:
        if isinstance(obj, str):
            obj = Path(obj)

        if not obj.exists():
            raise FileNotFoundError(f"{obj} does not exist.")

        issymlink = obj.is_symlink()
        isfile = obj.is_file()
        isdir = obj.is_dir()

        mode = obj.stat().st_mode
        if issymlink:
            tgt = obj.readlink()

        match [issymlink, isfile, isdir]:
            case [True, _, _] | [False, True, False]:
                exc = _remove_symlink_or_file(obj, error_callback=error_callback)
                excs = [exc] if exc is not None else []

            case [False, False, True]:
                excs = _remove_dir(obj, strict=strict, error_callback=error_callback)

            case _:
                symlink_info = "a symlink" if issymlink else "not a symlink"
                file_info = "a file" if isfile else "not a file"
                dir_info = "a directory" if isdir else "not a directory"
                exc = MatchError(f"Cannot solve object {obj}: {symlink_info}, {file_info}, and {dir_info}.")
                if error_callback:
                    error_callback(exc)
                excs = [exc]

        if return_exc:
            collected_excs.extend(excs)

        match [issymlink, isfile, isdir]:
            case [False, True, False]:
                obj.touch(mode=mode, exist_ok=True)
            case [False, False, True]:
                obj.mkdir(mode=mode, exist_ok=True)
            case [True, _, _]:
                obj.symlink_to(tgt, target_is_directory=isdir)

    except Exception as e:
        if error_callback:
            error_callback(e)
        collected_excs.append(e)

    if len(collected_excs) == 0 and success_callback:
        success_callback(f"`refresh_obj` done: {obj}.")

    if return_exc:
        return collected_excs
