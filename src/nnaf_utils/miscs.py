from .pytypes import *

def dict2str(**kwargs):
    return ', '.join([f"{k}={v}" for k, v in kwargs.items()])

def _remove_symlink_or_file(
    path: Path,
    error_callback: Callable[..., Any] = None,
) -> None | Exception:
    try:
        if not (path.is_symlink() or path.is_file()):
            raise ValueError(f"{path} is not a symlink or file, thus cannot be safely removed.")
        path.unlink(missing_ok=False)
    except Exception as e:
        if error_callback:
            error_callback(e)
        return e
    return None

def _remove_dir(
    path: Path,
    error_callback: Callable[..., Any] = None,
    strict: bool = False,
) -> Exception | Sequence[Exception]:
    # If strict, return exception immediately when occurs.
    # If not, collect exceptions and return at last.

    collected_excs = []

    for obj in path.iterdir():
        if obj.is_symlink() or obj.is_file():
            exc1 = _remove_symlink_or_file(obj, error_callback=error_callback)
            if exc1 is not None:
                if strict:
                    return exc1
                collected_excs.append(exc1)

        elif obj.is_dir():
            excs = _remove_dir(obj, error_callback=error_callback, strict=strict)
            if excs is not None:
                if strict:
                    return excs
                collected_excs.extend(excs)

        else:
            exc1 = ValueError(f"Object {obj} is neither a symlink, file, nor directory.")
            if strict:
                return exc1
            collected_excs.append(exc1)

    try:
        path.rmdir()
    except Exception as e:
        if error_callback:
            error_callback(e)
        if strict:
            return e
        collected_excs.append(e)

    return collected_excs or None

def refresh_obj(
    obj: StrPath,
    success_callback: Callable[..., Any] = None,
    error_callback: Callable[..., Any] = None,
    strict: bool = True,
    return_exception: bool = False,
) -> Exception | Sequence[Exception] | None:
    if isinstance(obj, str):
        obj = Path(obj)

    try:
        if not obj.exists():
            raise FileNotFoundError(f"Object {obj} does not exist.")
    except Exception as e:
        if error_callback:
            error_callback(e)
        return e if return_exception else None

    if obj.is_symlink() or obj.is_file():
        excs = _remove_symlink_or_file(obj, error_callback=error_callback)
    elif not obj.is_symlink() and obj.is_dir():
        excs = _remove_dir(obj, error_callback=error_callback, strict=strict)
    else:
        excs = ValueError(f"Object {obj} is neither a symlink, file, nor directory.")
        if error_callback:
            error_callback(excs)

    if excs is None and success_callback:
        success_callback(f"Object {obj} refreshed successfully.")
    return excs if return_exception else None
