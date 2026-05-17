import math

import pytest

from src.wallets.currency import rub, usd
from src.wallets.exceptions import NegativeValueException, NotComparisonException
from src.wallets.money import Money, Wallet


class TestMoney:
    @pytest.fixture
    def money1(self):
        return Money(value=1, currency=rub)

    @pytest.fixture
    def money2(self):
        return Money(value=2, currency=rub)

    @pytest.fixture
    def money3(self):
        return Money(value=3, currency=rub)

    def test_add(self, money1, money2, money3):
        assert money1 + money2 == money3

    def test_sub(self, money1, money2, money3):
        assert money3 - money2 == money1

    def test_other_currency(self, money1, money2, money3):
        with pytest.raises(NotComparisonException):
            Money(value=1, currency=rub) + Money(value=1, currency=usd)


class TestWallet:
    @pytest.fixture
    def money(self):
        return Money(value=500, currency=rub)

    @pytest.fixture
    def wallet(self, money):
        return Wallet(money)

    def test_get__exists(self, wallet, money):
        assert wallet[rub] == money

    def test_get__empty(self, wallet):
        assert wallet[usd] == Money(value=0, currency=usd)

    def test_del__exists(self, wallet):
        del wallet[rub]
        assert rub not in wallet.currencies

    def test_del__empty(self, wallet):
        del wallet[usd]
        assert usd not in wallet.currencies

    def test_len_currencies(self, wallet):
        assert len(wallet) == 1

    def test_contains(self, wallet):
        assert rub in wallet
        assert usd not in wallet

    def test_add(self, wallet):
        wallet.add(Money(value=100, currency=rub)).add(Money(value=200, currency=rub))
        assert wallet[rub] == Money(value=800, currency=rub)

    def test_sub(self, wallet):
        wallet.sub(Money(value=100, currency=rub)).sub(Money(value=200, currency=rub))
        assert wallet[rub] == Money(value=200, currency=rub)

    def test_sub__negative(self, wallet):
        with pytest.raises(NegativeValueException):
            wallet.sub(Money(value=math.inf, currency=rub))
