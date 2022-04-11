import typing

from flytekit import task, workflow
from typing import Tuple


@task
def t1(
    a: int,
) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):  # type:ignore
    return a + 2, "world"


@task
def t2(a: str, b: str) -> str:
    return b + a


@workflow
def my_wf(a: int, b: str) -> Tuple[int, str]:
    x, y = t1(a=a)
    d = t2(a=y, b=b)
    return x, d


if __name__ == "__main__":
    print(f"Running my_wf(a=50, b='hello') {my_wf(a=50, b='hello')}")
