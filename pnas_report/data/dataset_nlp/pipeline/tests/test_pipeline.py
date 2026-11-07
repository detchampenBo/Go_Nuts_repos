"""Fake-data test of get_guardian_articles.py: fake Transfermarkt CSVs, a fake
Guardian API (no network) and hand-written cache files. Run from any folder:
    python tests/test_pipeline.py
"""
import contextlib
import gzip
import importlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parents[1] / "get_guardian_articles.py"
RUN = Path(__file__).resolve().parent / "run"
KEY = "SECRET-KEY-123"


def banner(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        check.failed += 1
check.failed = 0


# ------------------------------------------------------------------ fake Transfermarkt data
ALPHA, BETA, GAMMA, DELTA, EPS = 1, 2, 3, 4, 5        # clubs
NAMES = {ALPHA: "Alpha FC", BETA: "Beta United", GAMMA: "Gamma SC", DELTA: "Delta Town", EPS: "Eps"}

PLAYERS = [  # player_id, name, first, last, dob, position
    (101, "Matija Nastasić", "Matija", "Nastasić", "1993-03-28", "Defender"),
    (102, "Pépé Vieux", "Pépé", "Vieux", "1980-01-01", "Midfield"),
    (103, "Carlos Medio", "Carlos", "Medio", "1988-06-15", "Midfield"),
    (104, "Bob Relegated", "Bob", "Relegated", "1995-01-01", "Attack"),
    (105, "Ed Birthday", "Ed", "Birthday", "1990-07-01", "Attack"),
    (106, "Al Almostthirty", "Al", "Almostthirty", "1990-07-02", "Attack"),
    (107, "Too Old", "Too", "Old", "1977-07-01", "Goalkeeper"),
    (108, "Kid Young", "Kid", "Young", "1997-01-01", "Attack"),
    (109, "Lou Loan", "Lou", "Loan", "1995-05-05", "Defender"),
    (110, "Lars Øverby", "Lars", "Øverby", "1996-02-02", "Attack"),
    (111, "Sam Same", "Sam", "Same", "1995-01-01", "Defender"),
    (112, "Cheap Guy", "Cheap", "Guy", "1995-01-01", "Defender"),
    (113, "Nan Value", "Nan", "Value", "1995-01-01", "Defender"),
    (114, "Early Bird", "Early", "Bird", "1995-01-01", "Defender"),
    (115, "Late Comer", "Late", "Comer", "1995-01-01", "Defender"),
    (116, "June Thirty", "June", "Thirty", "1995-01-01", "Defender"),
    (117, "Long Loan", "Long", "Loan", "1993-01-01", "Defender"),
    (354361, "Frank Anguissa", "Frank", "Anguissa", "1995-11-16", "Midfield"),
    (119, "No Birthday", "No", "Birthday", None, "Defender"),
]
TRANSFERS = [  # player_id, date, from, to, fee, market value
    (101, "2012-08-31", GAMMA, ALPHA, 15e6, 12e6),   # young 19 -> keep
    (102, "2014-07-01", GAMMA, DELTA, 0, 3e6),       # old 34 free -> keep
    (103, "2015-08-01", GAMMA, BETA, 4e6, 5e6),      # Beta in PL 2015 -> keep (middle 27)
    (104, "2016-08-01", GAMMA, BETA, 4e6, 5e6),      # Beta NOT in PL 2016 -> drop
    (105, "2014-07-01", GAMMA, ALPHA, 1e6, 3e6),     # 24th birthday ON the date -> 24 young
    (106, "2020-07-01", GAMMA, ALPHA, 1e6, 3e6),     # turns 30 the next day -> 29 middle
    (107, "2014-07-01", GAMMA, ALPHA, 0, 3e6),       # 37 -> drop
    (108, "2014-07-01", GAMMA, ALPHA, 1e6, 3e6),     # 17 -> drop
    (109, "2016-08-01", ALPHA, GAMMA, 0, 3e6),       # loan out (Gamma not PL)
    (109, "2017-06-30", GAMMA, ALPHA, 0, 3e6),       # loan return -> drop
    (109, "2017-07-01", ALPHA, DELTA, 20e6, 9e6),    # real sale -> keep
    (110, "2018-08-01", GAMMA, ALPHA, 0, 8e6),       # loan in -> keep (young 22)
    (110, "2019-06-30", ALPHA, GAMMA, 0, 8e6),       # loan return to Gamma (not PL dest)
    (110, "2019-07-01", GAMMA, ALPHA, 30e6, 10e6),   # paid buy after loan -> keep (KEEP_PAID)
    (111, "2015-07-01", ALPHA, ALPHA, 0, 3e6),       # same club -> drop
    (112, "2015-07-01", GAMMA, ALPHA, 1e6, 1.5e6),   # market value < 2m -> drop
    (113, "2015-07-01", GAMMA, ALPHA, 1e6, None),    # market value unknown -> drop
    (114, "2012-06-30", GAMMA, ALPHA, 1e6, 3e6),     # season 2011 -> drop
    (115, "2025-07-01", GAMMA, ALPHA, 1e6, 3e6),     # season 2025 -> drop
    (116, "2025-06-30", GAMMA, ALPHA, 1e6, 3e6),     # season 2024 -> keep
    (117, "2013-01-01", ALPHA, GAMMA, 0, 3e6),       # loan out
    (117, "2015-03-15", GAMMA, ALPHA, 0, 3e6),       # 803 days later -> NOT a loan return -> keep
    (354361, "2018-08-09", GAMMA, ALPHA, 24.85e6, 18e6),  # alias player -> keep
    (119, "2015-07-01", GAMMA, ALPHA, 1e6, 3e6),     # no date of birth -> drop
]
EXPECTED_SIGNINGS = {"101_20120831", "102_20140701", "103_20150801", "105_20140701",
                     "106_20200701", "109_20170701", "110_20180801", "110_20190701",
                     "116_20250630", "117_20150315", "354361_20180809"}


def write_fake_data(data):
    data.mkdir(parents=True, exist_ok=True)
    pname = {p[0]: p[1] for p in PLAYERS}
    t = pd.DataFrame([{
        "player_id": p, "transfer_date": d, "transfer_season": "", "from_club_id": f,
        "to_club_id": to, "from_club_name": NAMES[f], "to_club_name": NAMES[to],
        "transfer_fee": fee, "market_value_in_eur": mv, "player_name": pname[p]}
        for p, d, f, to, fee, mv in TRANSFERS])
    t.to_csv(data / "transfers.csv.gz", index=False, compression="gzip")
    pl = pd.DataFrame(PLAYERS, columns=["player_id", "name", "first_name", "last_name",
                                        "date_of_birth", "position"])
    pl["height_in_cm"] = 180
    pl.to_csv(data / "players.csv", index=False)          # plain .csv: tests data_file()
    games = []
    for season in range(2010, 2026):
        clubs = [ALPHA, DELTA] + ([BETA] if season == 2015 else [])
        for i, h in enumerate(clubs):
            for a in clubs[i + 1:]:
                games.append({"game_id": len(games), "competition_id": "GB1", "season": season,
                              "home_club_id": h, "away_club_id": a})
        games.append({"game_id": len(games), "competition_id": "ES1", "season": season,
                      "home_club_id": GAMMA, "away_club_id": EPS})
    pd.DataFrame(games).to_csv(data / "games.csv.gz", index=False, compression="gzip")


# ------------------------------------------------------------------ fake Guardian corpus
def art(aid, date, headline, body, tones=("news",), api_type="article"):
    return {"id": f"football/{aid}", "type": api_type, "sectionId": "football",
            "webPublicationDate": f"{date}T10:00:00Z", "webTitle": headline,
            "webUrl": f"https://www.theguardian.com/football/{aid}",
            "fields": {"headline": headline, "byline": "Fake Writer", "bodyText": body,
                       "wordcount": str(len(body.split())), "trailText": "trail"},
            "tags": [{"id": f"tone/{t}", "type": "tone"} for t in tones]
                    + [{"id": "football/premierleague", "type": "keyword"}]}


FILLER = " ".join(f"Filler sentence number {i} is here." for i in range(18))
CORPUS = [
    # Nastasić (101): transfer 2012-08-31
    art("n-before", "2012-05-01", "City scout defenders",
        "City are watching Matija Nastasić. He is 19. Other clubs too."),               # before
    art("n-sign", "2012-08-31", "Manchester City sign Nastasić",
        "Manchester City have signed Matija Nastasić from Fiorentina. Nastasić said he was happy. "
        "He trained on Friday. The fee was undisclosed."),                              # around, headline
    art("n-report", "2012-09-20", "City 2-0 Test",
        "City won. Matija Nastasic made his debut. His passing was neat. Nastasić was booked. "
        "He looked calm. " + FILLER, tones=("matchreports",)),                          # after, accent-free
    # mixed-age: names Nastasić (young) and Pépé Vieux (old, transfer 2014-07-01)
    art("live-mixed", "2013-08-01", "Pre-season friendly - live!",
        "Matija Nastasić starts. Pépé Vieux on the bench. " + FILLER,
        tones=("minutebyminute",), api_type="liveblog"),
    art("vieux-int", "2014-08-10", "Pépé Vieux: I still have the legs",
        "Pépé Vieux spoke to us. He is 34. Vieux has played 500 games.", tones=("interview",)),
    # Medio (103): low share, not focus
    art("medio-low", "2016-01-10", "Beta's season review",
        FILLER + " Carlos Medio was solid. " + FILLER, tones=("features",)),
    # Øverby (110): signings 2018-08-01 and 2019-07-01 -> overlapping windows
    art("o-dec18", "2018-12-01", "Øverby shines", "Lars Øverby scored twice. He is fast."),
    art("o-may19", "2019-05-01", "Alpha to make Øverby deal permanent",
        "Alpha will buy Lars Overby. The fee is 30m."),                                 # accent-free
    art("o-jan20", "2020-01-15", "Øverby injured", "Lars Øverby is out for six weeks."),
    # Anguissa (alias only)
    art("ang", "2018-09-01", "Fulham midfielder settles in",
        "André-Frank Zambo Anguissa has impressed. Anguissa covers ground. His tackling stands out."),
    # outside every window -> must never be returned
    art("ancient", "2005-01-01", "Matija Nastasić youth", "Matija Nastasić as a boy."),
]
for i in range(5):  # extra Nastasić articles to force pagination (page-size 2 in the test)
    CORPUS.append(art(f"n-extra{i}", f"2013-0{i + 1}-15", f"Note {i}",
                      f"Matija Nastasić trained. Other news {i}."))


class FakeResp:
    def __init__(self, status, payload=None):
        self.status_code, self._p = status, payload
        self.url = f"https://fake/search?api-key={KEY}"

    def json(self):
        return self._p


class FakeAPI:
    """Stands in for requests.Session.get; `script` = list of status codes to
    return before behaving normally (e.g. [503, 503] or [429])."""
    def __init__(self, page_size_seen=None):
        self.calls, self.script, self.params_seen = 0, [], []

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        self.params_seen.append(dict(params))
        if self.script:
            code = self.script.pop(0)
            if code == "network":
                import requests
                raise requests.ConnectionError(f"failed for {url}?api-key={params['api-key']}")
            return FakeResp(code, {"message": "error"})
        if params.get("api-key") != KEY:
            return FakeResp(401, {"message": "Unauthorized"})
        phrases = re.findall(r'"([^"]+)"', params["q"])
        hits = [a for a in CORPUS
                if params["from-date"] <= a["webPublicationDate"][:10] <= params["to-date"]
                and any(p in a["fields"]["headline"] + " " + a["fields"]["bodyText"] for p in phrases)]
        hits.sort(key=lambda a: a["webPublicationDate"])
        size, page = int(params["page-size"]), int(params["page"])
        pages = max(1, -(-len(hits) // size))
        return FakeResp(200, {"response": {"status": "ok", "total": len(hits), "pages": pages,
                                           "currentPage": page,
                                           "results": hits[(page - 1) * size: page * size]}})


@contextlib.contextmanager
def captured():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        yield buf
    print(buf.getvalue(), end="")


# ------------------------------------------------------------------ the test
def main():
    if RUN.exists():
        shutil.rmtree(RUN)
    RUN.mkdir(parents=True)
    shutil.copy(SRC, RUN / SRC.name)
    write_fake_data(RUN / "data")
    sys.path.insert(0, str(RUN))
    import get_guardian_articles as g          # the Jupyter way
    importlib.reload(g)
    import time as _time
    sleeps = []
    g.time.sleep = lambda s: sleeps.append(s)  # no real waiting in the test

    # ---------------------------------------------------------- select (command line)
    banner("STEP 1  select   (run as: python get_guardian_articles.py select)")
    r = subprocess.run([sys.executable, SRC.name, "select"], cwd=RUN, capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout, r.stderr)
    s = pd.read_csv(RUN / "signings.csv")
    check(set(s.signing_id) == EXPECTED_SIGNINGS,
          f"selected exactly the expected {len(EXPECTED_SIGNINGS)} signings "
          f"(extra: {set(s.signing_id) - EXPECTED_SIGNINGS}, missing: {EXPECTED_SIGNINGS - set(s.signing_id)})")
    age = s.set_index("signing_id")
    check(age.loc["105_20140701", "age_at_transfer"] == 24 and age.loc["105_20140701", "age_group"] == "young",
          "birthday on transfer date counts (24 -> young)")
    check(age.loc["106_20200701", "age_at_transfer"] == 29 and age.loc["106_20200701", "age_group"] == "middle",
          "one day before 30th birthday -> 29 (middle)")
    check(age.loc["102_20140701", "age_group"] == "old", "34-year-old -> old")
    check(age.loc["354361_20180809", "name_variants"] ==
          "Frank Anguissa|Zambo Anguissa|André-Frank Zambo Anguissa|Andre-Frank Zambo Anguissa",
          "ALIASES + accent-free alias in name_variants")
    check(age.loc["110_20180801", "name_variants"] == "Lars Øverby|Lars Overby", "Ø -> O in plain()")
    pat = g.name_pattern(g.match_terms(["N'Golo Kanté", "N'Golo Kante"], "Kanté"))
    check(bool(pat.search("Chelsea’s N’Golo Kanté ran.")) and bool(pat.search("Kante ran."))
          and not pat.search("Kantés") and not pat.search("kanté"),
          "name matching: curly/straight apostrophe, accent-free surname, whole words, case-sensitive")
    check(list(s.columns) == ["signing_id", "player_id", "name", "first_name", "last_name", "name_variants",
                              "date_of_birth", "age_at_transfer", "age_group", "position", "transfer_date",
                              "season", "from_club_id", "from_club_name", "to_club_id", "to_club_name",
                              "transfer_fee", "market_value_in_eur"], "signings.csv columns = spec")

    # strict spec heuristic: the paid buy after a loan return is dropped
    g.LOAN_RETURN_KEEP_PAID = False
    with contextlib.redirect_stdout(io.StringIO()):
        strict = g.select()
    check("110_20190701" not in set(strict.signing_id),
          "with LOAN_RETURN_KEEP_PAID=False the paid buy after a loan return is excluded (spec verbatim)")
    g.LOAN_RETURN_KEEP_PAID = True
    with contextlib.redirect_stdout(io.StringIO()):
        g.select()

    # missing columns -> clear error listing the columns found
    banner("select with a broken players file (missing column)")
    pl = pd.read_csv(RUN / "data" / "players.csv")
    pl.drop(columns="date_of_birth").to_csv(RUN / "data" / "players.csv", index=False)
    r = subprocess.run([sys.executable, SRC.name, "select"], cwd=RUN, capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout + r.stderr)
    check(r.returncode == 1 and "missing columns ['date_of_birth']" in r.stderr
          and "Columns found:" in r.stderr and "Traceback" not in r.stderr,
          "clear error, columns listed, no traceback")
    pl.to_csv(RUN / "data" / "players.csv", index=False)

    # ---------------------------------------------------------- fetch (fake API)
    banner("STEP 2  fetch   (fake API: 1st call 503, then OK; page-size 2 to force pagination)")
    import requests
    api = FakeAPI()
    requests.Session.get = lambda self, url, params=None, timeout=None: api.get(url, params, timeout)
    g.PAGE_SIZE = 2
    os.environ.pop("GUARDIAN_API_KEY", None)
    with captured() as out:
        g.fetch()
    check("API key missing or invalid" in out.getvalue() and api.calls == 0, "no key -> clear message, no calls")

    os.environ["GUARDIAN_API_KEY"] = KEY
    api.script = [503]
    with captured() as out:
        res = g.fetch(limit=4)
    check(res["fetched"] == 4 and "retry 1/3" in out.getvalue(), "503 retried, 4 signings fetched (limit=4)")
    check(10 in sleeps and 1.1 in sleeps, "10 s backoff and 1.1 s pause used")
    check(KEY not in out.getvalue(), "API key never printed")
    d = json.loads((g.CACHE / "101_20120831.json").read_text(encoding="utf-8"))
    check(list(d)[0] == "query_version" and d["query_version"] == 2 and "fetched_at_utc" in d
          and d["window_from"] == "2011-09-01" and d["window_to"] == "2013-08-31"
          and d["query"] == '"Matija Nastasić" OR "Matija Nastasic"',
          f"cache file has query_version=2, fetched_at_utc, ±365-day window, query {d['query']}")
    check(d["pages"] == 5 and d["n_articles"] == 9,
          f"pagination followed: {d['pages']} pages, {d['n_articles']} articles (outside-window article not returned)")
    first = next(x for x in api.params_seen if x["q"].startswith('"Matija'))
    check(first["section"] == "football" and first["order-by"] == "oldest"
          and first["show-fields"] == "headline,byline,bodyText,wordcount,trailText"
          and first["show-tags"] == "tone,keyword", "request params match the spec")

    banner("fetch hits HTTP 429 part-way (daily limit)")
    calls_before = api.calls
    orig = api.get
    n = {"i": 0}

    def get_then_429(url, params=None, timeout=None):
        n["i"] += 1
        return orig(url, params, timeout) if n["i"] <= 2 else FakeResp(429, {"message": "limit"})
    requests.Session.get = lambda self, url, params=None, timeout=None: get_then_429(url, params, timeout)
    with captured() as out:
        res = g.fetch()
    check(res["stopped"] and "HTTP 429" in out.getvalue() and res["remaining"] > 0,
          "429 -> clean stop with summary, nothing raised")
    n_cached = len(list(g.CACHE.glob("*.json")))
    check(not list(g.CACHE.glob("*.tmp")), "no half-written files left behind")

    banner("fetch again next day (resume)")
    requests.Session.get = lambda self, url, params=None, timeout=None: api.get(url, params, timeout)
    (g.CACHE / "103_20150801.json").write_text(json.dumps({"query_version": 1, "signing_id": "103_20150801",
                                                           "articles": []}), encoding="utf-8")
    with captured() as out:
        res = g.fetch()
    check(res["remaining"] == 0 and res["fetched"] == len(EXPECTED_SIGNINGS) - n_cached + 1,
          f"resume skipped {n_cached - 1} cached signings and re-fetched the query_version=1 file")
    check(json.loads((g.CACHE / "103_20150801.json").read_text(encoding="utf-8"))["query_version"] == 2,
          "old-version cache file replaced")

    banner("fetch with a bad key / API down")
    for f in list(g.CACHE.glob("116_*.json")):
        f.unlink()
    os.environ["GUARDIAN_API_KEY"] = "wrong"
    with captured() as out:
        res = g.fetch()
    check("API key missing or invalid" in out.getvalue() and res["fetched"] == 0, "401 -> stop with key message")
    os.environ["GUARDIAN_API_KEY"] = KEY
    api.script = [500, "network", 502, 503]
    with captured() as out:
        res = g.fetch()
    check("after 3 retries" in out.getvalue() and KEY not in out.getvalue(),
          "5xx/network 4 times -> stop after 3 retries; key not leaked from the exception text")
    with contextlib.redirect_stdout(io.StringIO()):
        g.fetch()
    check(all(g.cached_version(g.cache_path(x)) == 2 for x in EXPECTED_SIGNINGS), "all signings cached")

    # an old-format cache file (as in guardian_cache/) mixed in must be ignored by build
    (g.CACHE / "999_20150101.json").write_text(json.dumps({"signing_id": "999_20150101", "articles": []}),
                                               encoding="utf-8")

    # ---------------------------------------------------------- build
    banner("STEP 3  build   (run as: python get_guardian_articles.py build; no pyarrow here -> CSV)")
    r = subprocess.run([sys.executable, SRC.name, "build"], cwd=RUN, capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout, r.stderr)
    arts_path = RUN / ("articles.parquet" if (RUN / "articles.parquet").exists() else "articles.csv")
    arts = pd.read_parquet(arts_path) if arts_path.suffix == ".parquet" else pd.read_csv(arts_path)
    ap = pd.read_csv(RUN / "article_player.csv")
    sent = pd.read_csv(RUN / "sentences.csv")
    check(arts.article_id.is_unique and len(arts) == len(CORPUS) - 1,
          f"articles deduplicated: {len(arts)} unique (corpus minus the out-of-window one)")
    check(list(arts.columns) == ["article_id", "url", "publication_date", "headline", "byline", "wordcount",
                                 "tones", "keywords", "article_type", "body_text"], "articles columns")
    t = arts.set_index("article_id").article_type
    check(t["football/live-mixed"] == "liveblog" and t["football/n-report"] == "matchreport"
          and t["football/vieux-int"] == "interview" and t["football/medio-low"] == "features"
          and t["football/n-sign"] == "news", "tone -> article_type mapping")

    L = ap.set_index(["article_id", "signing_id"])
    check(not ap.duplicated(["article_id", "signing_id"]).any(), "article_player key unique")
    row = L.loc[("football/n-sign", "101_20120831")]
    check(row.period == "around" and row.days_from_transfer == 0 and row.name_in_headline
          and row.is_focus_article, "announcement article: around, name in headline, focus")
    row = L.loc[("football/n-before", "101_20120831")]
    check(row.period == "before" and row.days_from_transfer == -122, "before period, days = -122")
    row = L.loc[("football/n-report", "101_20120831")]
    check(row.period == "after" and row.mentions == 2 and row.total_sentences == 23,
          f"accent-free + surname matched: mentions {row.mentions} of {row.total_sentences} sentences")
    check(row.player_sentences == "Matija Nastasic made his debut. His passing was neat. "
                                  "Nastasić was booked. He looked calm.",
          "follow-on rule: He/His sentence after a naming sentence is added once")
    check(round(row.share_of_sentences, 4) == round(2 / 23, 4) and not row.is_focus_article,
          "share 2/23 < 0.10 and no name in headline -> not focus")
    row = L.loc[("football/medio-low", "103_20150801")]
    check(row.mentions == 1 and not row.is_focus_article, "low-share article is not focus")
    check(round(L.loc[("football/n-sign", "101_20120831")].age_at_article, 2) == 19.43,
          "age_at_article = (publication - birth)/365.25")

    mixed = ap[ap.article_id == "football/live-mixed"]
    check(len(mixed) == 2 and mixed.mixed_age_article.all() and (mixed.n_tracked_players_in_article == 1).all(),
          "liveblog naming a young and an old player: mixed_age_article, 1 other tracked player")
    check(not ap[ap.article_id == "football/n-sign"].mixed_age_article.any(), "single-player article not mixed")

    ov = ap[ap.player_id == 110].set_index("article_id")
    check(ov.loc["football/o-dec18", "signing_id"] == "110_20180801"
          and ov.loc["football/o-may19", "signing_id"] == "110_20190701"
          and ov.loc["football/o-jan20", "signing_id"] == "110_20190701",
          "dedup rule: each Øverby article kept once, linked to the nearest transfer")
    check(len(ov) == 3 and ov.loc["football/o-dec18", "overlapping_window"]
          and ov.loc["football/o-may19", "overlapping_window"]
          and not ov.loc["football/o-jan20", "overlapping_window"],
          "overlapping_window true only where the other signing's ±365 window covers the date")
    check(not ap[ap.player_id == 101].overlapping_window.any(), "no overlap for single-signing player")
    ang = ap[ap.player_id == 354361]
    check(len(ang) == 1 and ang.mentions.iloc[0] == 2,
          "alias-only article found and counted (Zambo Anguissa / Anguissa)")
    check(set(sent.columns) == {"article_id", "signing_id", "player", "period", "days_from_transfer",
                                "age_at_article", "age_group_at_transfer", "article_type",
                                "match_kind", "sentence"}, "sentences columns = spec")
    check(set(zip(sent.article_id, sent.signing_id)) <= set(zip(ap.article_id, ap.signing_id))
          and not ((sent.article_id == "football/o-may19") & (sent.signing_id == "110_20180801")).any(),
          "sentences only for links kept after dedup")
    check((sent.match_kind == "follow-on").sum() > 0, "follow-on sentences labelled")

    # ---------------------------------------------------------- PermissionError (Excel lock)
    banner("build while article_player.csv is open in Excel (simulated lock)")
    before = (RUN / "article_player.csv").read_bytes()
    real_locked = g._locked
    g._locked = lambda paths: [p for p in paths if p.name == "article_player.csv"]
    with captured() as out:
        res = g.build()
    g._locked = real_locked
    check("close article_player.csv in Excel and re-run build" in out.getvalue() and res is None
          and (RUN / "article_player.csv").read_bytes() == before
          and not list(RUN.glob("*.tmp")),
          "locked file detected BEFORE the slow work starts; nothing changed, no traceback")

    banner("file gets locked while build runs (os.replace fails at the end)")
    real_replace = g.os.replace

    def replace(src, dst):
        if str(dst).endswith("article_player.csv"):
            raise PermissionError(13, "Permission denied")
        return real_replace(src, dst)
    g.os.replace = replace
    with captured() as out:
        g.build()
    g.os.replace = real_replace
    check("close article_player.csv in Excel and re-run build" in out.getvalue()
          and "Written: articles.csv, sentences.csv" in out.getvalue(),
          "clear message; the other files are still written")
    for t in RUN.glob("*.tmp"):
        t.unlink()

    # ---------------------------------------------------------- streaming in small chunks
    banner("build with CHUNK_ROWS = 3 (articles and sentences written in many small chunks)")
    ref_ap = pd.read_csv(RUN / "article_player.csv")
    with contextlib.redirect_stdout(io.StringIO()):
        g.build()
    ref_art, ref_sent = pd.read_csv(RUN / "articles.csv"), pd.read_csv(RUN / "sentences.csv")
    g.CHUNK_ROWS = 3
    with contextlib.redirect_stdout(io.StringIO()):
        g.build()
    g.CHUNK_ROWS = 2000
    a2, s2 = pd.read_csv(RUN / "articles.csv"), pd.read_csv(RUN / "sentences.csv")
    check(a2.equals(ref_art) and s2.equals(ref_sent)
          and pd.read_csv(RUN / "article_player.csv").equals(ref_ap)
          and not list(RUN.glob("*.tmp")),
          f"identical output with tiny chunks ({len(a2)} articles, {len(s2)} sentences); no temp files left")

    # ---------------------------------------------------------- parquet path (fake pyarrow)
    banner("build with pyarrow available (stand-in module, pyarrow not installable here)")
    import types
    calls = {"tables": 0, "rows": 0, "path": None, "closed": False}
    pa = types.ModuleType("pyarrow")
    pq = types.ModuleType("pyarrow.parquet")
    pa.string = pa.float64 = lambda: "t"
    pa.timestamp = lambda unit: "ts"
    pa.schema = lambda fields: [f[0] for f in fields]
    class _T:
        @staticmethod
        def from_pandas(df, schema=None, preserve_index=False):
            assert list(df.columns) == schema
            return df
    pa.Table = _T
    class _W:
        def __init__(self, path, schema):
            calls["path"] = path
            open(path, "w").close()
        def write_table(self, t):
            calls["tables"] += 1; calls["rows"] += len(t)
        def close(self):
            calls["closed"] = True
    pq.ParquetWriter = _W
    pa.parquet = pq
    sys.modules["pyarrow"], sys.modules["pyarrow.parquet"] = pa, pq
    with contextlib.redirect_stdout(io.StringIO()) as out:
        g.build()
    del sys.modules["pyarrow"], sys.modules["pyarrow.parquet"]
    check(calls["path"].endswith("articles.parquet.tmp") and calls["closed"]
          and calls["rows"] == len(ref_art) and (RUN / "articles.parquet").exists()
          and "articles.parquet" in out.getvalue(),
          "articles.parquet is written (in chunks) when pyarrow is installed")
    (RUN / "articles.parquet").unlink(missing_ok=True)

    # ---------------------------------------------------------- validate
    banner("STEP 4  validate   (run as: python get_guardian_articles.py validate)")
    (RUN / "articles.parquet").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, SRC.name, "validate"], cwd=RUN, capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout, r.stderr)
    samp = pd.read_csv(RUN / "check_focus_sample.csv")
    check(r.returncode == 0 and len(samp) == len(ap) and "truly_about_player (y/n)" in samp.columns
          and samp.headline.notna().all(), f"check_focus_sample.csv written ({len(samp)} rows = all links, < 100)")

    banner(f"RESULT: {'ALL TESTS PASSED' if not check.failed else f'{check.failed} FAILED'}")
    return check.failed


if __name__ == "__main__":
    sys.exit(main())
