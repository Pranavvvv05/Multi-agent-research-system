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
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
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
            "error": str | None   # only present if success is False
        }
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "success": False,
            "error": str(e),
        }

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove junk tags that aren't actual article content
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"

    # Grab text from <p> tags first, fallback to full page text if empty
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    if not text:
        text = soup.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "title": title,
        "content": text,
        "success": True,
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