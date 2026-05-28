from typing import AsyncGenerator, no_type_check
import aiohttp
import pdfplumber
import pandas as pd
from pdfplumber.page import Page
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import date as DatetimeDate
import logging
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
import traceback

import time

from exceptions import TableNotFoundToExtract
from database import TradeResultsOrm, get_async_db_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Pdf = list[list[str]] | None
Xls = list[list[str]] | None
Tasks = list[asyncio.Task]
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0"}
SPIMEX_HTML_PAGE_URL = "https://spimex.com/markets/oil_products/trades/results/"
HTTP_SEMAPHORE = asyncio.Semaphore(20)


def _is_desired_table_there(page: Page) -> bool:
    res = page.extract_text()
    s_res = res.split("\n")
    if "Единица измерения: Метрическая тонна" in s_res:
        if s_res[-1] != "Единица измерения: Метрическая тонна":
            return True
    return False


# @no_type_check
async def _create_table_result_orm(table: Pdf | Xls, date: DatetimeDate, session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        async with session.begin():
            for i in range(len(table)):
                table_results_orm = TradeResultsOrm()
                table_results_orm.exchange_product_id = table[i][0]
                table_results_orm.exchange_product_name = table[i][1]
                table_results_orm.oil_id = table[i][0][:4]
                table_results_orm.delivery_basis_id = table[i][0][4:7]
                table_results_orm.delivery_basis_name = table[i][2]
                table_results_orm.delivery_type_id = table[i][0][-1]
                if table[i][3] in ("-", "nan"):
                    table_results_orm.volume = None
                else:
                    num_without_colons = table[i][3].split(",")
                    table_results_orm.volume = int("".join(num_without_colons))
                if table[i][4] in ("-", "nan"):
                    table_results_orm.total = None
                else:
                    num_without_colons = table[i][4].split(",")
                    table_results_orm.total = int("".join(num_without_colons))
                if table[i][-1] in ("-", "nan"):
                    table_results_orm.count = None
                else:
                    num_without_colons = table[i][-1].split(",")
                    table_results_orm.volume = int("".join(num_without_colons))
                table_results_orm.date = date

                session.add(table_results_orm)
                await session.flush()


# @no_type_check
async def _load_first_page(page: Page, date: DatetimeDate, session_factory: async_sessionmaker[AsyncSession]) -> None:
    table: Pdf = page.extract_tables()[-1]
    if not table:
        raise TableNotFoundToExtract("Table for extraction not found")
    await _create_table_result_orm(table[2:], date, session_factory)


def extract_from_pdf(pdf_bytes: bytes, page_num: int):
    tables = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf_parsed:
        for i in range(page_num + 1, len(pdf_parsed.pages)):
            page = pdf_parsed.pages[i]
            extract_start = time.time()
            table: Pdf = page.extract_table()
            extract_end = time.time()
            logger.info(f"Extract time: {extract_end - extract_start}")
            if not table:
                continue
            tables.append(table)

    return tables


# @no_type_check
async def parse_pdf(
    pdf_url: str,
    date: DatetimeDate,
    session_factory: async_sessionmaker[AsyncSession],
    ac: aiohttp.ClientSession,
    executor: ProcessPoolExecutor
):
    async with HTTP_SEMAPHORE:
        try:
            async with ac.get(pdf_url) as pdf_doc_response:
                if not pdf_doc_response.status == 200:
                    raise ValueError("Wrong response")
                pdf_doc_response_content = await pdf_doc_response.read()
                pdf_doc_response_bytes = BytesIO(pdf_doc_response_content)
                start = time.time()
                try:
                    pdf_parsed = pdfplumber.open(pdf_doc_response_bytes)
                except Exception as e:
                    logger.error(f"pdf parse error: {str(e)}")
                    return
                end = time.time()

            logger.info(f"pdfplumber's open implements in {end - start} time units")
            page_num: int = 0
            if len(pdf_parsed.pages) == 0:
                logger.error(f"Empty PDF: {pdf_url}")
                pdf_parsed.close()
                return
            page: Page = pdf_parsed.pages[page_num]
            while not _is_desired_table_there(page):
                page_num += 1
                page: Page = pdf_parsed.pages[page_num]

            await _load_first_page(page, date, session_factory)

            loop = asyncio.get_running_loop()
            tables = await loop.run_in_executor(executor, extract_from_pdf, pdf_doc_response_content, page_num)
            create_table_tasks = []
            for table in tables:
                task = asyncio.create_task(_create_table_result_orm(table, date, session_factory))
                create_table_tasks.append(task)
            await asyncio.gather(*create_table_tasks)

            pdf_parsed.close()
        except asyncio.CancelledError:
            logger.warning(f"Task cancelled for {pdf_url}")
        except Exception as e:
            logger.error(f"Error: {str(e)}")


def _find_markers(content: BytesIO, before_table_marker: str, after_table_marker: str) -> tuple[int, int, int]:
    file = pd.read_excel(content, engine='xlrd')
    rows_lst = file.values.tolist()

    before_table_marker_id = 0
    after_table_marker_id = 0
    for i, row in enumerate(rows_lst):
        if row[1] == before_table_marker:
            before_table_marker_id = i
            break

    for j in range(len(rows_lst) - 1, -1, -1):
        if rows_lst[j][1] == after_table_marker:
            after_table_marker_id = j
            break

    return before_table_marker_id, after_table_marker_id, len(rows_lst)


def _extract_from_xls(xls_bytes: bytes):
    with BytesIO(xls_bytes) as bio:
        before, after, n_rows = _find_markers(bio, "Единица измерения: Метрическая тонна", "Итого:")
        bio.seek(0)
        df = pd.read_excel(bio, engine='xlrd', skiprows=before + 3, skipfooter=n_rows - after)
        df_to_list = df.values.tolist()
        # Пропускаю первый элемент в excel таблице, потому что он null
        res_lst = []
        for l in df_to_list:
            res_lst.append(l[1:])
        return res_lst


async def parse_xls(
    xls_url: str,
    date: DatetimeDate,
    session_factory: async_sessionmaker[AsyncSession],
    ac: aiohttp.ClientSession,
    executor: ProcessPoolExecutor,
):
    async with HTTP_SEMAPHORE:
        try:
            async with ac.get(xls_url) as response:
                if response.status != 200:
                    raise ValueError("Wrong response")
                content = await response.read()
                loop = asyncio.get_running_loop()
                df_to_list = await loop.run_in_executor(executor, _extract_from_xls, content)

                df_to_list = [list(map(str, l)) for l in df_to_list]
                await _create_table_result_orm(df_to_list, date, session_factory)

        except asyncio.CancelledError:
            logger.warning(f"Task cancelled for {xls_url}")
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(f"Error: {str(e)}")


async def parse(
    current_url: str,
    url_prefix: str,
    ac: aiohttp.ClientSession,
    session_factory: async_sessionmaker[AsyncSession],
    executor: ProcessPoolExecutor,
) -> tuple[Tasks, bool]:
    is_pdf = True
    is_end = False
    async with ac.get(current_url) as response:
        if response.status != 200:
            logger.error(f"Failed to load {current_url}")
            return [], False

        soup = BeautifulSoup(await response.text(), 'html.parser')

    content = soup.find("div", class_="accordeon-inner")
    if not content:
        logger.error("Page not found")
        return [], False

    trade_results = content.find_all("div", class_="accordeon-inner__wrap-item")
    tasks = []

    for trade_res in trade_results:
        if not trade_res:
            continue

        link_elem = trade_res.find("a", class_="accordeon-inner__item-title link pdf")
        if not link_elem:
            xls_link_elem = trade_res.find("a", class_="accordeon-inner__item-title link xls")
            if xls_link_elem:
                link_elem = xls_link_elem
                is_pdf = False
            else:
                is_pdf = True
                continue

        link_full = url_prefix + link_elem.get('href')

        date_elem = trade_res.find("div", class_="accordeon-inner__item-inner__title")
        if not date_elem or not date_elem.p or not date_elem.p.span:
            continue

        date = date_elem.p.span.text[:10]
        day, month, year= map(int, date.split("."))

        try:
            if int(year) < 2023:
                is_end = True
                break
        except ValueError:
            continue

        if is_pdf:
            task = asyncio.create_task(
                parse_pdf(link_full, DatetimeDate(year, month, day), session_factory, ac, executor)
            )
        else:
            task = asyncio.create_task(
                parse_xls(link_full, DatetimeDate(year, month, day), session_factory, ac, executor)
            )
        tasks.append(task)

    return await asyncio.gather(*tasks), is_end


# @no_type_check
async def main() -> None:
    db_engine_gen: AsyncGenerator[async_sessionmaker[AsyncSession]] = get_async_db_session()
    session_factory: async_sessionmaker[AsyncSession] = await anext(db_engine_gen)
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        async with aiohttp.ClientSession(headers=HEADERS, timeout=aiohttp.ClientTimeout(total=60)) as ac:
            logger.info("http запрос на страницу биржи...")

            url_prefix = "https://spimex.com"
            current_url = SPIMEX_HTML_PAGE_URL

            page_number = 1

            while True:
                logger.info(f"Обработка страницы: page={page_number}, url={current_url}")

                tasks, is_end = await parse(current_url, url_prefix, ac, session_factory, executor)
                if is_end:
                    break
                # Поиск ссылки на след страницу
                async with ac.get(current_url) as response:
                    soup = BeautifulSoup(await response.text(), 'html.parser')

                pagination = soup.find("div", class_="bx-pagination")
                if not pagination:
                    logger.info("Пагинация не найдена")
                    break

                next_page_li = pagination.find("li", class_="bx-pag-next")
                if not next_page_li:
                    logger.info("Следующая страница не найдена")
                    break

                next_page_url = next_page_li.a.get('href')
                logger.info(f"next_page_url = {next_page_url}")
                if not next_page_url:
                    break

                current_url = url_prefix + next_page_url
                page_number += 1

            await ac.close()

        try:
            await anext(db_engine_gen)
        except StopAsyncIteration:
            pass


if __name__ == "__main__":
    asyncio.run(main())
