from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import time


SEARCH_URL = (
    "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&"
    "ie=utf8&query=%EB%B0%98%EB%8F%84%EC%B2%B4"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
}
MAX_ARTICLES = 5


def get_soup(url):
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=15) as response:
        return BeautifulSoup(response.read(), "html.parser")


def get_news_links(search_soup):
    links = []
    selectors = (
        "a.news_tit, .news_area a[href], "
        "a[href*='n.news.naver.com/mnews/article/']"
    )
    for tag in search_soup.select(selectors):
        link = urljoin(SEARCH_URL, tag.get("href", ""))
        title = tag.get("title") or tag.get_text(" ", strip=True)

        if title and link.startswith(("http://", "https://")):
            if not any(item["url"] == link for item in links):
                links.append({"title": title, "url": link})

        if len(links) >= MAX_ARTICLES:
            break
    return links


def get_article_content(article_soup):
    content_tag = article_soup.select_one(
        "#dic_area, #newsct_article, article, .article_body, .article_body_content"
    )
    if content_tag is None:
        return ""

    for tag in content_tag.select("script, style, iframe, .reporter_area"):
        tag.decompose()

    return content_tag.get_text(" ", strip=True)


def crawl_articles():
    search_soup = get_soup(SEARCH_URL)
    news_links = get_news_links(search_soup)
    articles = []

    for index, news in enumerate(news_links, start=1):
        try:
            article_soup = get_soup(news["url"])
            title_tag = article_soup.select_one(
                "meta[property='og:title'], h2#title_area, "
                "h2.media_end_head_headline"
            )
            if title_tag and title_tag.name == "meta":
                title = title_tag.get("content", "").strip()
            else:
                title = title_tag.get_text(" ", strip=True) if title_tag else news["title"]
            content = get_article_content(article_soup)

            articles.append({
                "title": title,
                "url": news["url"],
                "content": content,
            })
            print(f"[{index}] {title}")
            print(content[:200] + ("..." if len(content) > 200 else ""))
            print()
        except Exception as error:
            print(f"기사 수집 실패: {news['url']} ({error})")

        time.sleep(1)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "네이버 뉴스"

    headers = ["번호", "기사 제목", "기사 URL", "기사 본문"]
    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for index, article in enumerate(articles, start=1):
        worksheet.append([
            index,
            article["title"],
            article["url"],
            article["content"],
        ])

    worksheet.column_dimensions["A"].width = 8
    worksheet.column_dimensions["B"].width = 45
    worksheet.column_dimensions["C"].width = 70
    worksheet.column_dimensions["D"].width = 120
    for row in worksheet.iter_rows(min_row=2):
        row[3].alignment = Alignment(wrap_text=True, vertical="top")

    workbook.save("naver_result.xlsx")

    print(f"총 {len(articles)}개의 기사를 naver_result.xlsx에 저장했습니다.")


if __name__ == "__main__":
    crawl_articles()