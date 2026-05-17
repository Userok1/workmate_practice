from dataclasses import dataclass
from abc import ABC


@dataclass
class Order:
    """There is no need to describe anything here."""


class Discount(ABC):
    "Discount abstract class"

    def __init__(self, order: Order) -> None:
        self.order = order


class FixDiscount(Discount):
    def __init__(self, order: Order, fixed: int) -> None:
        super().__init__(order)
        self.fixed = fixed


class PercentageDiscount(Discount):
    def __init__(self, order: Order, percentage: float):
        super().__init__(order)
        self.percentage = percentage


class LoyaltyDiscount(Discount):
    def __init__(self, order: Order, loyalty: float) -> None:
        super().__init__(order)
        self.loyalty = loyalty


class DiscountApplier:
    def __init__(self, order: Order, discount_list: set[Discount]) -> None:
        self.order = order
        self.discount_list = discount_list

    def apply(self) -> None:
        "Application of discount to order"


def get_discounts_from_order(order: Order) -> set[Discount]:
    "Getting a set of discounts from Order"
    # Getting discounts from order data.
    discounts: set[Discount] = ... # type: ignore
    return discounts
