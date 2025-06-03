from dataclasses import dataclass

from joblib import delayed

from .pytype import *


def run_in_another_thread(
    func,
    *args,
    timeout: float = 5,
    success_callback: Callable[[Any], None] = None,
    error_callback: Callable[[Exception], None] = None,
    **kwargs,
) -> None:
    """Run function in another thread with a timeout.

    Run a synchronous or asynchronous function in a non-blocking way using a separate
    thread with a limited timeout. If successful, calls the success callback with the
    result. If an error occurs, calls the error callback with the exception.

    """
    try:
        import asyncio
        import inspect
        import threading
        from concurrent.futures import ThreadPoolExecutor

        assert timeout is not None and timeout > 0

        def run():
            with ThreadPoolExecutor(max_workers=1) as executor:
                if inspect.iscoroutinefunction(func):

                    def wrap_afunc():
                        return asyncio.run(asyncio.wait_for(func(*args, **kwargs), timeout=timeout))

                    future = executor.submit(wrap_afunc)
                else:
                    future = executor.submit(func, *args, **kwargs)
                result = future.result(timeout=timeout)

            if success_callback is not None:
                success_callback(result)

        thread = threading.Thread(target=run)
        thread.start()

    except Exception as e:
        if error_callback is not None:
            error_callback(e)


@dataclass
class JoblibConfig:
    """Configuration for joblib parallel processing.

    Attributes:
        n_jobs (int): Number of parallel jobs. Default: ``1``.
        return_as (Literal["generator", "list", "generator_unordered"]): Return type. Default: ``"list"``.
        prefer (Literal["threads", "processes", None]): Preferred backend. Default: ``None``.
        require (Literal["sharedmem", None]): Required host method. Default: ``None``.
        pre_dispatch (str | int): Pre-dispatching jobs. Default: ``"2 * n_jobs"``.
        batch_size (Literal["auto"] | int): Batch size for processing. Default: ``"auto"``.

    """

    n_jobs: int = 1
    return_as: str = "list"
    prefer: str = None
    require: str = None
    pre_dispatch: str | int = "2 * n_jobs"
    batch_size: str | int = "auto"


def create_parallel_executor(
    n_jobs: int = 1,
    return_as: Literal["generator", "list", "generator_unordered"] = "list",
    prefer: Literal["threads", "processes", None] = None,
    require: Literal["sharedmem", None] = None,
    pre_dispatch: str | int = "2 * n_jobs",
    batch_size: Literal["auto"] | int = "auto",
):
    from joblib import Parallel, parallel_config

    with parallel_config(n_jobs=n_jobs, prefer=prefer, require=require):
        executor = Parallel(
            return_as=return_as,
            pre_dispatch=pre_dispatch,
            batch_size=batch_size,
        )
    return executor
