from typing import no_type_check
import requests
import pdfplumber
from pdfplumber.page import Page
from sqlalchemy.orm import sessionmaker, Session
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import date as DatetimeDate
import logging

import time

from exceptions import PageNotFoundError, TableNotFoundToExtract
from database import session_factory, TradeResultsOrm, Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF = list[list[str]] | None

SPIMEX_HTML_PAGE_URL = "https://spimex.com/markets/oil_products/trades/results/"


def _is_desired_table_there(page: Page) -> bool:
    res = page.extract_text()
    s_res = res.split("\n")
    if "Единица измерения: Метрическая тонна" in s_res:
        if s_res[-1] != "Единица измерения: Метрическая тонна":
            return True
    return False


@no_type_check
def _create_table_result_orm(table: PDF, date: DatetimeDate, session: Session):
    for i in range(len(table)):
        table_results_orm = TradeResultsOrm()
        table_results_orm.exchange_product_id = table[i][0]
        table_results_orm.exchange_product_name = table[i][1]
        table_results_orm.oil_id = table[i][0][:4]
        table_results_orm.delivery_basis_id = table[i][0][4:7]
        table_results_orm.delivery_basis_name = table[i][2]
        table_results_orm.delivery_type_id = table[i][0][-1]
        table_results_orm.volume = table[i][3] if table[i][3] != "-" else None
        table_results_orm.total = table[i][4] if table[i][4] != "-" else None
        table_results_orm.count = table[i][-1] if table[i][-1] != "-" else None
        table_results_orm.date = date

        session.add(table_results_orm)
        session.flush()


@no_type_check
def _load_first_page(page: Page, date: DatetimeDate, session: Session) -> None:
    table: PDF = page.extract_tables()[-1]
    logger.info(f"First table rows: {len(table)}")
    if not table:
        raise TableNotFoundToExtract("Table for extraction not found")
    _create_table_result_orm(table[2:], date, session)


@no_type_check
def parse_pdf(pdf_url: str, date: DatetimeDate, session_factory: sessionmaker[Session]):
    with session_factory() as session:
        pdf_doc_response = requests.get(pdf_url)
        pdf_doc_response_bytes = BytesIO(pdf_doc_response.content)
        start = time.time()
        pdf_parsed = pdfplumber.open(pdf_doc_response_bytes)
        end = time.time()
        logger.info(f"pdfplumber's open implements in {end - start} time units")
        page_num = 0
        page: Page = pdf_parsed.pages[page_num]
        while not _is_desired_table_there(page):
            page_num += 1
            page: Page = pdf_parsed.pages[page_num]
        _load_first_page(page, date, session)

        for i in range(page_num + 1, len(pdf_parsed.pages)):
            page = pdf_parsed.pages[i]
            table: PDF = page.extract_table()
            logger.info(f"Table rows: {len(table)}")
            if not table:
                raise TableNotFoundToExtract("Table for extraction not found")
            _create_table_result_orm(table, date, session)

        session.commit()


@no_type_check
def main() -> None:
    logger.info("http запрос на страницу биржи...")
    page_html_response = requests.get(SPIMEX_HTML_PAGE_URL)
    logger.info("Парсинг html документа страницы...")
    soup = BeautifulSoup(page_html_response.text, 'html.parser')
    url_prefix = "https://spimex.com/"

    while True:
        content = soup.find("div", class_="accordeon-inner")
        if not content:
            raise PageNotFoundError("Content page not found")

        trade_results = content.find_all("div", class_="accordeon-inner__wrap-item")
        for trade_res in trade_results:
            pdf_link = trade_res.find("a", class_="accordeon-inner__item-title link pdf")["href"]
            pdf_link_full = url_prefix + pdf_link
            logger.info(f"pdf ссылка: {pdf_link_full}")
            date = trade_res.find("div", class_="accordeon-inner__item-inner__title").p.span.text[:10]
            logger.info(f"Дата: {date}")
            if int(date[-4:]) < 2023:
                break
            logger.info("Парсинг pdf...")
            day, month, year = map(int, date.split("."))
            parse_pdf(pdf_link_full, DatetimeDate(year, month, day), session_factory)

        pagination = soup.find("div", class_="bx-pagination")
        logger.info("Получение ссылки на след страницу...")
        next_page_url = pagination.find("li", class_="bx-pag-next").a.get('href')
        logger.info(f"Ссылка на след страницу: {next_page_url}")
        logger.info("http запрос на страницу биржи...")
        next_page_url_full = url_prefix + next_page_url
        page_html_response = requests.get(next_page_url_full)
        logger.info("Парсинг html документа страницы...")
        soup = BeautifulSoup(page_html_response.text, 'html.parser')


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    main()
    # URL = "https://spimex.com/files/trades/result/pdf/oil/oil_20260525162000.pdf?r=5074"
    # pdf_page = requests.get(URL)
    # b = BytesIO(pdf_page.content)
    # pdf = pdfplumber.open(b)
    # page = pdf.pages[1]
    # res = page.extract_table()
    # print(len(res))
    # for l in res:
    #     print(l)
