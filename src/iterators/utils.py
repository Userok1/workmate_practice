from dataclasses import dataclass, field
from itertools import batched
from typing import Iterable, TypeAlias, Generator, Self

SomeRemoteData: TypeAlias = int


@dataclass
class Query:
    per_page: int = 3
    page: int = 1


@dataclass
class Page:
    per_page: int = 3
    results: Iterable[SomeRemoteData] = field(default_factory=list)
    next: int | None = None


def request(query: Query) -> Page:
    data = [i for i in range(0, 10)]
    chunks = list(batched(data, query.per_page))
    return Page(
        per_page=query.per_page,
        results=chunks[query.page - 1],
        next=query.page + 1 if query.page < len(chunks) else None,
    )


class RetrieveRemoteData:
    def __init__(self, per_page: int) -> None:
        self.per_page = per_page
        self.page: Page = request(Query(per_page=self.per_page, page=0))

    def __iter__(self) -> Generator[SomeRemoteData, None, None]:
        def return_gen():
            while self.page.next:
                self.page = request(Query(per_page=self.per_page, page=self.page.next))
                yield from self.page.results
        return return_gen()

    def __next__(self) -> Generator[SomeRemoteData, None, None]:
        return iter(self)


class Fibo:
    def __init__(self, n: int) -> None:
        self.n = n
        self.a = 0
        self.b = 1
        self.cnt = 1

    def __iter__(self) -> Self:
        return self

    def __next__(self, stop_iter_return=None) -> int:
        while self.cnt < self.n + 1:
            val = self.a
            self.a, self.b = self.b, self.a + self.b
            self.cnt += 1
            # return val
            return val
        raise StopIteration
