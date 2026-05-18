from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from datetime import date
from typing import Any

from bs4 import BeautifulSoup


# @dataclass(init=False, slots=True, frozen=True)
# class ParserParams:
#     def __init__(self, **kwargs):
#         for key, value in kwargs:
#             self.__dict__[key] = value


class HtmlParser(ABC):
    "Html parser basic class"
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "html.parser")

    @abstractmethod
    def parse(self, html: str) -> Any:
        "Parse data"
        pass


class HtmlLinksParser(HtmlParser):
    def parse(self, html: str, start_date: date, second_date: date) -> list[tuple[str, date]]:
        """
        Парсит ссылки на бюллетени с одной страницы:
        <a class="accordeon-inner__item-title link xls" href="/upload/reports/oil_xls/oil_xls_20240101_test.xls">link1</a>
        """
        # TODO: возможно стоит разделить блоки кода на методы (Single Responsibility Princple),
        # то есть например: вынести валидацию xls файла (1), вынести парсинг даты (2)
        start_date: date | None = kwargs.get("start_date")
        end_date: date | None = kwargs.get("end_date")
        url: str | None = kwargs.get("url")
        if not start_date or not end_date or not url:
            raise ValueError("Required params not provided")

        # Добавил аннотации типов для results
        results: list[tuple[str, datetime._Date]] = []
        # TODO: возможно стоит вынести части ссылки в атрибуты класса
        links = self.soup.find_all("a", class_="accordeon-inner__item-title link xls")

        for link in links:
            href = link.get("href")
            if not href:
                continue

            # href -> href_without_url_params
            # TODO: (1) возможно следует вынести в отдельный метод валидацию xls файла
            href_without_url_params = href.split("?")[0]
            if "/upload/reports/oil_xls/oil_xls_" not in href_without_url_params or \
                not href_without_url_params.endswith(".xls"):
                continue

            try:
                # Изменил название переменной date -> report_date_str
                # TODO: (2) возможно следует вынести парсинг даты в отдельный метод
                report_date_str = href.split("oil_xls_")[1][:8]
                # file -> report_date
                report_date = datetime.datetime.strptime(report_date_str, "%Y%m%d").date()
                if start_date <= report_date <= end_date:
                    # u -> parsed_url
                    parsed_url = report_date_str if report_date_str.startswith("http") else f"https://spimex.com{report_date_str}"
                    results.append((parsed_url, report_date))
                else:
                    print(f"Ссылка {report_date_str} вне диапазона дат")
            # Exception -> ValueError
            except ValueError as e:
                print(f"Не удалось извлечь дату из ссылки {href_without_url_params}: {e}")

        return results



# def parse_page_links(html: str, start_date: date, end_date: date, url: str):
#     """
#     Парсит ссылки на бюллетени с одной страницы:
#     <a class="accordeon-inner__item-title link xls" href="/upload/reports/oil_xls/oil_xls_20240101_test.xls">link1</a>
#     """
#     results = []
#     soup = BeautifulSoup(html, "html.parser")
#     links = soup.find_all("a", class_="accordeon-inner__item-title link xls")
#
#     for link in links:
#         href = link.get("href")
#         if not href:
#             continue
#
#         href = href.split("?")[0]
#         if "/upload/reports/oil_xls/oil_xls_" not in href or not href.endswith(".xls"):
#             continue
#
#         try:
#             date = href.split("oil_xls_")[1][:8]
#             file = datetime.datetime.strptime(date, "%Y%m%d").date()
#             if start_date <= file <= end_date:
#                 u = href if href.startswith("http") else f"https://spimex.com{href}"
#                 results.append((u, file))
#             else:
#                 print(f"Ссылка {href} вне диапазона дат")
#         except Exception as e:
#             print(f"Не удалось извлечь дату из ссылки {href}: {e}")
#
#     return results
