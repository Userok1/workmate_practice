import pytest
from httpx import AsyncClient


class TestGetLastTradingDates:
    @pytest.mark.anyio
    async def test_get_last_trading_dates__success(self, tc: AsyncClient, dates_data):
        response = await tc.get("/trades/dates/?days=5")

        assert response.status_code == 200
        assert response.json() == dates_data

    @pytest.mark.parametrize("days", ["0", "-5"])
    @pytest.mark.anyio
    async def test__get_last_trading_dates__invalid_days(self, days, tc: AsyncClient):
        response = await tc.get(f"/trades/dates/?days={days}")

        assert response.status_code == 422
        res = response.json()
        assert res["detail"][0]["msg"] == "Input should be greater than 0"
        assert res["detail"][0]["input"] == days


class TestGetDynamics:
    @pytest.mark.anyio
    async def test_get_dynamics__success(self, tc: AsyncClient):
        response = await tc.get(
            "/trades/2026-05-01/2026-07-01/?oil_id=A692&delivery_type_id=F&delivery_basis_id=NIL"
        )

        assert response.status_code == 200
        results = response.json()
        assert results["page"] == 1
        assert results["page_size"] == 100
        for result in results["trade_results"]:
            assert result["oil_id"] == "A692"
            assert result["delivery_type_id"] == "F"
            assert result["delivery_basis_id"] == "NIL"

    @pytest.mark.anyio
    async def test_get_dynamics__invalid_date(self, tc: AsyncClient):
        response = await tc.get(
            "/trades/invalid_date000/2026-07-01/?oil_id=A692&delivery_type_id=F&delivery_basis_id=NIL"
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_get_dynamics__not_found(self, tc: AsyncClient):
        response = await tc.get(
            "/trades/3050-05-01/3090-07-01/?oil_id=A692&delivery_type_id=F&delivery_basis_id=NIL"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Trade results not found"


class TestGetResults:
    @pytest.mark.anyio
    async def test_trade_results__success(self, tc: AsyncClient):
        response = await tc.get(
            "/trades/?page=1&page_size=10&oil_id=A692&delivery_type_id=F&delivery_basis_id=NIL"
        )

        assert response.status_code == 200
        results = response.json()
        assert results["page"] == 1
        assert results["page_size"] == 10
        for result in results["trade_results"]:
            assert result["oil_id"] == "A692"
            assert result["delivery_type_id"] == "F"
            assert result["delivery_basis_id"] == "NIL"

    @pytest.mark.anyio
    async def test_trade_results__not_found(self, tc: AsyncClient):
        response = await tc.get("/trades/?page=4&page_size=10&oil_id=invalid_oil_id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Trading results not found"
