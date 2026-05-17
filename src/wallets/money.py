from dataclasses import dataclass
import decimal
import logging

from src.wallets.currency import Currency
from src.wallets.exceptions import NegativeValueException, NotComparisonException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(repr=True)
class Money:
    value: decimal.Decimal
    currency: Currency

    def __post_init__(self):
        if self.value < 0:
            raise NegativeValueException("Attr value can't be negative")

    def __add__(self, other):
        self._check_same_currency(other)
        return Money(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other):
        self._check_same_currency(other)
        if self.value < other.value:
            raise NegativeValueException("Result of subtraction can not be negative")
        return Money(value=self.value - other.value, currency=self.currency)

    def _check_same_currency(self, other):
        if not (self.currency == other.currency):
            raise NotComparisonException("Operation forbidden between defferent currencies")


class Wallet:
    def __init__(self, money: Money) -> None:
        # self.balance: dict[str, Money] = {money.currency: Money(value=0, currency=money.currency)}
        self.balance: dict[Currency, Money] = {}
        # self.balance[money.currency] += money
        self.add(money)

    def add(self, money: Money):
        if not money.currency in self.currencies:
            self.balance[money.currency] = Money(value=0, currency=money.currency)
        self.balance[money.currency] += money
        return self

    def sub(self, money: Money):
        if not money.currency in self.balance.keys():
            self.balance[money.currency] = Money(value=0, currency=money.currency)
        self.balance[money.currency] -= money
        return self

    @property
    def currencies(self) -> set:
        return set(self.balance.keys())

    def __getitem__(self, key):
        return self.balance.setdefault(key, Money(value=0, currency=key))

    def __setitem__(self, key, value: Money):
        assert key == value.currency, (key, value.currency)
        self.balance[key] = value

    def __delitem__(self, key):
        if key in self:
            del self.balance[key]

    def __len__(self):
        return len(self.currencies)

    def __contains__(self, value):
        return value in self.currencies

    # def __str__(self):
    #     return str({key: str(self.balance[key]) for key in self.currencies})
    #
    # def __repr__(self):
    #     return f"Wallet(balance={str(self.balance)}, currencies={str(self.currencies)})"
