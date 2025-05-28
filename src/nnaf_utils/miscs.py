from .pytypes import *

def dict2str(**kwargs):
    kwargs.items()
    return ', '.join([f"{k}={v}" for k, v in kwargs.items()])

def refresh_obj(obj: StrPath, leave_empty: bool = True):
    if isinstance(obj, str):
        obj = Path(obj)

    if obj.is_symlink():
        try:
            tgt = obj.resolve(strict=True)
            refresh_obj(tgt, leave_empty=leave_empty)
            if not leave_empty:
                try:
                    obj.unlink()
                except OSError:
                    pass
        except FileNotFoundError:
            try:
                obj.unlink()
            except OSError:
                pass

    elif obj.is_dir():
        for sub in obj.iterdir():
            refresh_obj(sub, leave_empty=False)
        if not leave_empty:
            try:
                obj.rmdir()
            except OSError:
                pass
    
    elif obj.is_file():
        try:
            obj.unlink()
        except OSError:
            pass
        if leave_empty:
            try:
                obj.touch()
            except OSError:
                pass
