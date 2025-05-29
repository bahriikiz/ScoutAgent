import requests
from bs4 import BeautifulSoup
import hashlib
import difflib

# Use a realistic browser User-Agent to avoid simple bot blocks
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )
}

def fetch_content(url: str) -> str:
    """
    Fetches the HTML content of the given URL with a browser-like header.
    Returns the HTML as a string, or raises RuntimeError on failure.
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            raise RuntimeError(
                f"Access denied (403) when fetching {url}. "
                "You may need authentication or a different User-Agent."
            )
        raise RuntimeError(f"Failed to fetch {url}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


def compute_hash(html: str) -> str:
    """
    Computes a SHA256 hash of the given HTML string.
    Returns the hex digest.
    """
    return hashlib.sha256(html.encode('utf-8')).hexdigest()


def compute_diff(old_html: str, new_html: str) -> str:
    """
    Computes a unified diff between two HTML strings.
    Returns the diff as a string.
    """
    old_lines = old_html.splitlines(keepends=True)
    new_lines = new_html.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='old', tofile='new')
    return ''.join(diff)
