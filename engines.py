"""Search engine definitions for hard-enforced default search policies.

Each engine provides URL templates compatible with Chromium's
DefaultSearchProvider* group policies and Firefox's policies.json
SearchEngines section. ``{searchTerms}`` is the standard placeholder.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchEngine:
    """A search engine entry usable in browser policies."""

    name: str
    keyword: str
    search_url: str
    suggest_url: str = ""


SEARCH_ENGINES: tuple[SearchEngine, ...] = (
    SearchEngine(
        name="Google",
        keyword="google.com",
        search_url="https://www.google.com/search?q={searchTerms}",
        suggest_url="https://www.google.com/complete/search?client=firefox&q={searchTerms}",
    ),
    SearchEngine(
        name="Bing",
        keyword="bing.com",
        search_url="https://www.bing.com/search?q={searchTerms}",
        suggest_url="https://api.bing.com/osjson.aspx?query={searchTerms}",
    ),
    SearchEngine(
        name="DuckDuckGo",
        keyword="duckduckgo.com",
        search_url="https://duckduckgo.com/?q={searchTerms}",
        suggest_url="https://duckduckgo.com/ac/?q={searchTerms}&type=list",
    ),
    SearchEngine(
        name="Brave Search",
        keyword="brave.com",
        search_url="https://search.brave.com/search?q={searchTerms}",
        suggest_url="https://search.brave.com/api/suggest?q={searchTerms}",
    ),
    SearchEngine(
        name="Startpage",
        keyword="startpage.com",
        search_url="https://www.startpage.com/sp/search?query={searchTerms}",
        suggest_url="https://www.startpage.com/suggest?query={searchTerms}",
    ),
    SearchEngine(
        name="Mojeek",
        keyword="mojeek.com",
        search_url="https://www.mojeek.com/search?q={searchTerms}",
        suggest_url="https://www.mojeek.com/suggest?q={searchTerms}",
    ),
    SearchEngine(
        name="Qwant",
        keyword="qwant.com",
        search_url="https://www.qwant.com/?q={searchTerms}",
        suggest_url="https://api.qwant.com/v3/suggest/?q={searchTerms}&client=opensearch",
    ),
    SearchEngine(
        name="Ecosia",
        keyword="ecosia.org",
        search_url="https://www.ecosia.org/search?q={searchTerms}",
        suggest_url="https://ac.ecosia.org/autocomplete?q={searchTerms}&type=list",
    ),
    SearchEngine(
        name="Yahoo",
        keyword="yahoo.com",
        search_url="https://search.yahoo.com/search?p={searchTerms}",
        suggest_url="https://search.yahoo.com/sugg/gossip/gossip-us-ura/?output=sd1&command={searchTerms}",
    ),
    SearchEngine(
        name="SearXNG",
        keyword="searx.be",
        search_url="https://searx.be/search?q={searchTerms}",
        suggest_url="https://searx.be/autocompleter?q={searchTerms}",
    ),
)

ENGINE_NAMES: tuple[str, ...] = tuple(e.name for e in SEARCH_ENGINES)


def get_engine(name: str) -> SearchEngine:
    """Return engine by display name.

    Args:
        name: Display name, e.g. "DuckDuckGo".

    Returns:
        Matching SearchEngine.

    Raises:
        KeyError: If no engine with that name exists.
    """
    for engine in SEARCH_ENGINES:
        if engine.name == name:
            return engine
    raise KeyError(f"Unknown search engine: {name}")
