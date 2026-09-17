import csv
import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


NAVER_STOCK_URL = "https://stock.naver.com/market/stock/kr"
FINANCE_LIST_URL = "https://finance.naver.com/sise/sise_market_sum.naver"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


def get_soup(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")


def clean_text(tag):
    return re.sub(r"\s+", " ", tag.get_text(" ", strip=True))


def get_stock_code(stock_tag):
    href = stock_tag.get("href", "")
    code = re.search(r"code=(\d{6})", href)
    return code.group(1) if code else ""


def crawl_stocks(market=0, pages=5):
    """네이버 금융의 시가총액 표를 BeautifulSoup으로 수집합니다.

    market: 0=코스피, 1=코스닥
    """
    stocks = []

    for page in range(1, pages + 1):
        soup = get_soup(
            FINANCE_LIST_URL,
            params={"sosok": market, "page": page},
        )
        table = soup.select_one("table.type_2")
        if table is None:
            raise RuntimeError("주식 목록 표를 찾지 못했습니다.")

        for row in table.select("tr"):
            cells = row.select("td")
            stock_tag = row.select_one("a.tltle")
            if stock_tag is None or len(cells) < 12:
                continue

            stocks.append(
                {
                    "종목명": clean_text(stock_tag),
                    "종목코드": get_stock_code(stock_tag),
                    "현재가": clean_text(cells[1]),
                    "전일비": clean_text(cells[2]),
                    "등락률": clean_text(cells[3]),
                    "액면가": clean_text(cells[4]),
                    "시가총액": clean_text(cells[5]),
                    "상장주식수": clean_text(cells[6]),
                    "외국인비율": clean_text(cells[7]),
                    "거래량": clean_text(cells[8]),
                    "PER": clean_text(cells[10]),
                    "ROE": clean_text(cells[11]),
                    "상세주소": urljoin(
                        "https://finance.naver.com", stock_tag.get("href", "")
                    ),
                }
            )

    return stocks


def check_requested_page():
    """사용자가 지정한 최신 증권 페이지의 정적 HTML 상태를 확인합니다."""
    soup = get_soup(NAVER_STOCK_URL)
    rows = soup.select("table tr")
    return {
        "url": NAVER_STOCK_URL,
        "table_count": len(soup.select("table")),
        "row_count": len(rows),
        "has_stock_rows": any(
            any(clean_text(cell) for cell in row.select("td")) for row in rows
        ),
    }


def save_results(stocks, filename="naver_stocks.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(stocks, file, ensure_ascii=False, indent=2)


def save_csv(stocks, filename="naver_stocks.csv"):
    if not stocks:
        return

    with open(filename, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=stocks[0].keys())
        writer.writeheader()
        writer.writerows(stocks)


if __name__ == "__main__":
    page_status = check_requested_page()
    print(f"요청 페이지 확인: {page_status}")
    if not page_status["has_stock_rows"]:
        print(
            "종목 행이 정적 HTML에 없습니다. "
            "현재 페이지는 JavaScript가 실행된 뒤 종목 데이터를 표시합니다."
        )
        print(
            "전체 종목 목록은 Selenium/Playwright로 브라우저를 실행하거나 "
            "네이버가 제공하는 데이터 API를 사용해야 합니다."
        )
    else:
        kospi = crawl_stocks(market=0, pages=2)
        kosdaq = crawl_stocks(market=1, pages=2)
        stocks = kospi + kosdaq
        save_results(stocks)
        save_csv(stocks)
        print(
            f"총 {len(stocks)}개 종목을 "
            "naver_stocks.json과 naver_stocks.csv에 저장했습니다."
        )