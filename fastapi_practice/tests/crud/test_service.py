import pytest
from datetime import date


from src.crud import service
from src.crud.service import read_trading_dates, read_results


class TestGetTradingDates:
    @pytest.mark.anyio
    async def test_get_trading_dates__success(self, dates_data, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()

        async def mock_cache_load(*args, **kwargs):
            return dates_data

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_trading_dates(*args, **kwargs):
                return dates_data

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        res = await read_trading_dates(5, mock_session_factory, mock_redis_client)
        assert res == dates_data

    @pytest.mark.anyio
    async def test_get_trading_dates__not_cached(self, dates_data, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()

        async def mock_cache_load(*args, **kwargs):
            return None

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_trading_dates(*args, **kwargs):
                return dates_data

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        res = await read_trading_dates(5, mock_session_factory, mock_redis_client)
        assert res == dates_data

    @pytest.mark.anyio
    async def test_get_trading_results__not_found(self, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()

        async def mock_cache_load(*args, **kwargs):
            return None

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_trading_dates(*args, **kwargs):
                return None

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        assert (
            await read_trading_dates(5, mock_session_factory, mock_redis_client) is None
        )


class TestGetResults:
    @pytest.mark.anyio
    async def test_get_results__success(self, filters, results_data, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()
        start_date = date(2026, 1, 1)
        end_date = date(2026, 2, 1)

        async def mock_cache_load(*args, **kwargs):
            return results_data

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_results(*args, **kwargs):
                return results_data

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        res = await read_results(
            filters, mock_session_factory, mock_redis_client, start_date, end_date
        )
        assert res == results_data

    @pytest.mark.anyio
    async def test_get_results__not_cached(self, filters, results_data, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()
        start_date = date(2026, 1, 1)
        end_date = date(2026, 2, 1)

        async def mock_cache_load(*args, **kwargs):
            return None

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_results(*args, **kwargs):
                return results_data

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        res = await read_results(
            filters, mock_session_factory, mock_redis_client, start_date, end_date
        )
        assert res == results_data

    @pytest.mark.anyio
    async def test_get_results__not_found(self, filters, monkeypatch):
        mock_session_factory = object()
        mock_redis_client = object()
        start_date = date(2026, 1, 1)
        end_date = date(2026, 2, 1)

        async def mock_cache_load(*args, **kwargs):
            return None

        async def mock_cache_dump(*args, **kwargs):
            return None

        class MockTradingResultsRepo:
            async def get_results(*args, **kwargs):
                return None

        monkeypatch.setattr(service, "cache_load", mock_cache_load)
        monkeypatch.setattr(service, "cache_dump", mock_cache_dump)
        monkeypatch.setattr(service, "TradingResultsRepository", MockTradingResultsRepo)

        assert (
            await read_results(
                filters, mock_session_factory, mock_redis_client, start_date, end_date
            )
            is None
        )
