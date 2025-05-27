from .pytypes import *

def dict2str(**kwargs):
    kwargs.items()
    return ', '.join([f"{k}={v}" for k, v in kwargs.items()])

def refresh_dir(dir: StrPath, leave_empty: bool = True):
    if isinstance(dir, str):
        dir = Path(dir)
    if dir.exists():
        for item in dir.iterdir():
            if item.is_dir():
                refresh_dir(item, leave_empty=False)
            else:
                item.unlink()
        if not leave_empty:
            dir.rmdir()
    elif leave_empty:
        dir.mkdir(parents=True, exist_ok=True)
