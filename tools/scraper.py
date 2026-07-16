"""
scraper.py
----------
Tool used by the Research Agent to fetch the FULL text content of a webpage,
web_search.py only gives you a short snippet. scraper.py goes to that URL
and pulls out the complete, cleaned text using requests + BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def scrape_url(url: str, timeout: int = 10) -> dict:
    """
    Fetches a webpage and extracts clean, readable text content.

    Returns a dict:
        {
            "url": str,
            "title": str | None,
            "content": str | None,
            "success": bool,
            "error": str | None,       # only present if success is False
            "blocked": bool            # True if the site returned 403/999
                                        # (bot-protection), so the UI can
                                        # show a clearer message than a
                                        # raw HTTP error.
        }
    """
    try:
        session = requests.Session()
        response = session.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        status_code = getattr(e.response, "status_code", None)
        blocked = status_code in (403, 999, 429)
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": str(e),
            "blocked": blocked,
        }

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove junk tags that aren't actual article content
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"

    # Grab text from <p> tags first, fallback to full page text if empty/small
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True))

    if len(text.strip()) < 100:
        text = soup.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "title": title,
        "content": text,
        "success": True,
        "blocked": False,
    }


def scrape_multiple(urls: list[str], timeout: int = 10) -> list[dict]:
    """
    Convenience function to scrape a list of URLs
    (e.g. the output of web_search()).
    """
    results = []
    for url in urls:
        results.append(scrape_url(url, timeout))
    return results


if __name__ == "__main__":
    test_url = "https://www.apple.com/iphone/"
    result = scrape_url(test_url)

    print(f"\nURL: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"Success: {result['success']}")
    print(f"\nContent:\n{result['content'][:500]}...\n")