from src.iterators.utils import Fibo, Query, RetrieveRemoteData, request


class TestFibo:
    def test(self):
        reference = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        results = [obj for obj in Fibo(n=10)]
        assert results == reference


class TestRetrieveRemoteData:
    def test(self):
        reference = request(Query(per_page=100, page=1))  # 1, 2, 3, 4, 5, 6, 7, 8, 9
        results = [obj for obj in RetrieveRemoteData(per_page=3)]
        assert results == list(reference.results)
