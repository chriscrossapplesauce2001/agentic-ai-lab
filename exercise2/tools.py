import os
import math
import numexpr
from ddgs import DDGS

# How many web-search results to return per query.
SEARCH_MAX_RESULTS = 5


# --- Tool 1: Web Search ---
def web_search(query: str) -> str:
    """Search the web for current information.

    Args:
        query: A search query string.

    Returns:
        Snippets with source URLs, or an error message.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=SEARCH_MAX_RESULTS))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"- {r['title']}: {r['body']} ({r['href']})")
        return "\n".join(lines)
    except Exception as exc:
        return f"Search error: {exc}"


# --- Tool 2: Calculator ---
def calculator(expression: str) -> str:
    """Calculate a math expression.

    Args:
        expression: A valid math expression like '2 + 2' or '(3.14 * 0.2 * 0.4**3) / 12'.
            Supports +, -, *, /, **, sqrt, sin, cos, log, pi, e.

    Returns:
        The numeric result, or an error message.
    """
    try:
        local_dict = {"pi": math.pi, "e": math.e}
        result = numexpr.evaluate(expression.strip(), global_dict={}, local_dict=local_dict)
        return f"Result: {float(result)}"
    except Exception as exc:
        return f"Error evaluating '{expression}': {exc}"


# --- Tool 3: File Reader ---
ALLOWED_DIR = os.path.dirname(os.path.abspath(__file__))


def read_file(filename: str) -> str:
    """Read a local text file.

    Args:
        filename: A filename like 'sample.txt'. Only files in the project directory can be read.

    Returns:
        The file contents (up to 10 000 chars), or an error message.
    """
    safe_name = os.path.basename(filename)
    filepath = os.path.join(ALLOWED_DIR, safe_name)
    if not os.path.isfile(filepath):
        return f"Error: File '{safe_name}' not found in project directory."
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(10_000)
        return content
    except Exception as exc:
        return f"Error reading '{safe_name}': {exc}"


# Name -> function dispatch map
tool_map = {
    "web_search": web_search,
    "calculator": calculator,
    "read_file": read_file,
}
