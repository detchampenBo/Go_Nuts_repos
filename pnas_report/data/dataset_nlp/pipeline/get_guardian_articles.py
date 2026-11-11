"""
Guardian coverage of Premier League signings — data acquisition pipeline.
Implements pipeline_spec.yaml (version 2), steps 1-4.

Steps
  select    Pick every signing INTO a Premier League club, seasons 2012/13 to
            2024/25, market value at transfer >= EUR 2m, aged 18-36 on the
            transfer date (young 18-24 / middle 25-29 / old 30-36).
            Same-club moves and loan returns are excluded.     -> signings.csv
  fetch     One Guardian API query per signing, 365 days before to 365 days
            after the transfer. Every signing is cached in guardian_cache_v2/,
            so you can stop at any time (e.g. on the daily limit, HTTP 429)
            and re-run: it continues where it stopped.
  build     Turn the cache into the analysis tables:
              articles.parquet   one row per unique article (falls back to
                                 articles.csv if parquet is not available)
              article_player.csv one row per (article, signing) link
              sentences.csv      one row per sentence about the player
  validate  Print the step-4 checks and write check_focus_sample.csv
            (100 random article_player rows to read by hand).

Before you run it
  1. Transfermarkt files (Kaggle "Football Data from Transfermarkt", dcaribou)
     in data/ next to this script: transfers, players, games (.csv or .csv.gz).
  2. pip install pandas requests pyarrow      (pyarrow is optional)
  3. Guardian key in the environment variable GUARDIAN_API_KEY:
        Windows (PowerShell):  $env:GUARDIAN_API_KEY = "your-key"
        Jupyter:               import os; os.environ["GUARDIAN_API_KEY"] = "your-key"

Run
  python get_guardian_articles.py select
  python get_guardian_articles.py fetch        (or: fetch 50  -> at most 50 signings)
  python get_guardian_articles.py build
  python get_guardian_articles.py validate

  or in Jupyter:  import get_guardian_articles as g;  g.select(); g.fetch(); ...
"""

import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# =================================================================== settings
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"                     # Transfermarkt CSVs go here
CACHE = HERE / "guardian_cache_v2"       # one JSON file per signing (new: v2)

SIGNINGS_CSV = HERE / "signings.csv"
ARTICLES_PARQUET = HERE / "articles.parquet"
ARTICLES_CSV = HERE / "articles.csv"     # used only if parquet cannot be written
ARTICLE_PLAYER_CSV = HERE / "article_player.csv"
SENTENCES_CSV = HERE / "sentences.csv"
FOCUS_SAMPLE_CSV = HERE / "check_focus_sample.csv"
ZERO_ARTICLES_CSV = HERE / "check_zero_articles.csv"

# --- step 1: selection
PL_COMPETITION_ID = "GB1"                # Premier League id in Transfermarkt
FIRST_SEASON, LAST_SEASON = 2012, 2024   # 2012 = 2012/13 ... 2024 = 2024/25
MIN_MARKET_VALUE_EUR = 2_000_000         # market_value_in_eur at transfer
LOAN_RETURN_DAYS = 730                   # loan-return heuristic look-back
LOAN_RETURN_KEEP_PAID = True             # a move with transfer_fee > 0 is never a loan return
                                         # (keeps e.g. Romero 2022, Odegaard 2021: loan -> return
                                         # -> permanent buy). False = spec heuristic verbatim.
AGE_GROUPS = [                           # (label, lowest, highest) completed years
    ("young", 18, 24),
    ("middle", 25, 29),
    ("old", 30, 36),
]
EXPECTED_COUNTS = {"young": 1250, "middle": 670, "old": 140}   # from the spec (approx.)

# Extra names the Guardian uses, keyed by Transfermarkt player_id.
# Add to this when validate lists a signing with 0 articles, then re-fetch
# that signing (delete its file in guardian_cache_v2/ and run fetch again).
ALIASES = {
    354361: ["Zambo Anguissa", "André-Frank Zambo Anguissa"],   # Frank Anguissa
    91845: ["Son Heung-min"],                                   # Heung-min Son
    81796: ["Ki Sung-yueng"],                                   # Sung-yueng Ki
    186186: ["Bobby Reid", "Bobby Decordova-Reid"],             # Bobby De Cordova-Reid
    369684: ["Rasmus Kristensen"],                              # Rasmus Nissen Kristensen
    1004327: ["Yang Min-hyeok"],                                # Min-hyeok Yang
    71271: ["Adrián"],                                          # Adrián San Miguel (goes by "Adrián")
    255744: ["Samir"],                                          # Samir Caetano (goes by "Samir")
}

# --- step 2: Guardian API
API_URL = "https://content.guardianapis.com/search"
API_KEY_ENV = "GUARDIAN_API_KEY"
WINDOW_DAYS = 365                        # days before AND after the transfer date
PAGE_SIZE = 200                          # API maximum
PAUSE_SECONDS = 1.1                      # between calls (free key: ~1 call/second)
RETRIES_5XX = 3                          # retries on HTTP 5xx / network errors
RETRY_BACKOFF_SECONDS = 10
TIMEOUT_SECONDS = 30
QUERY_VERSION = 2                        # stored in every cache file
SHOW_FIELDS = "headline,byline,bodyText,wordcount,trailText"
SHOW_TAGS = "tone,keyword"

# --- step 3: build
AROUND_DAYS = 7                          # "around" = -7 ... +7 days from transfer
FOCUS_SHARE = 0.10                       # is_focus_article if share >= this (or name in headline)
TONE_TO_TYPE = {                         # first match wins (order = priority)
    "tone/minutebyminute": "liveblog",
    "tone/matchreports": "matchreport",
    "tone/interview": "interview",
    "tone/comment": "comment",
    "tone/features": "features",
    "tone/blog": "blog",
    "tone/news": "news",
}

# --- step 4: validate
MIN_ARTICLES_PER_PERIOD = 3              # "balance" check: >= 3 in before AND after
FOCUS_SAMPLE_SIZE = 100
RANDOM_SEED = 2805


# =================================================================== helpers
class PipelineError(Exception):
    """A problem the user has to fix (missing file, missing columns, ...)."""


def data_file(name):
    """Find data/<name>.csv or data/<name>.csv.gz (Kaggle ships them gzipped)."""
    for ext in (".csv", ".csv.gz"):
        f = DATA / f"{name}{ext}"
        if f.exists():
            return f
    raise PipelineError(f"Could not find {name}.csv or {name}.csv.gz in {DATA}")


def need_columns(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise PipelineError(f"{name} is missing columns {missing}. "
                            f"Columns found: {list(df.columns)}")


def need_file(path, step):
    if not path.exists():
        raise PipelineError(f"{path.name} not found - run '{step}' first.")


def save_csv(df, path, step):
    """Write a CSV that Excel opens with accents intact. Returns True on success."""
    try:
        df.to_csv(path, index=False, encoding="utf-8-sig")
        return True
    except PermissionError:
        print(f"!! Could not write {path.name} (it is open in another program): "
              f"close {path.name} in Excel and re-run {step}.")
        return False


def season_of(date):
    """Football season a date belongs to: July 2019 to June 2020 -> 2019."""
    return date.year if date.month >= 7 else date.year - 1


def completed_years(born, on):
    """Age in completed years (vectorised over two datetime Series)."""
    had_birthday = (on.dt.month * 100 + on.dt.day) >= (born.dt.month * 100 + born.dt.day)
    return on.dt.year - born.dt.year - (~had_birthday).astype(int)


def age_group(age):
    if pd.isna(age):
        return None
    for label, lo, hi in AGE_GROUPS:
        if lo <= age <= hi:
            return label
    return None


_SPECIAL_LETTERS = str.maketrans({
    "ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "đ": "d", "Đ": "D", "ß": "ss",
    "æ": "ae", "Æ": "Ae", "œ": "oe", "Œ": "Oe", "ı": "i", "þ": "th", "Þ": "Th",
})


def plain(text):
    """Accent-free version of a name: 'Matija Nastasić' -> 'Matija Nastasic'."""
    text = str(text).translate(_SPECIAL_LETTERS)
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _unique(names):
    out = []
    for n in names:
        n = " ".join(str(n).replace('"', "").split())     # tidy spaces, no quotes
        if n and n not in out:
            out.append(n)
    return out


def name_variants(name, player_id=None):
    """Full name, accent-free full name, then manual aliases (and their plain forms)."""
    aliases = ALIASES.get(int(player_id), []) if pd.notna(player_id) else []
    names = _unique([name, plain(name)] + aliases + [plain(a) for a in aliases])
    # the Guardian prints N’Golo with a curly apostrophe; its search needs that form
    return _unique(names + [n.replace("'", "’") for n in names])


def match_terms(variants, last_name):
    """Strings that count as 'naming the player' in a text: all name variants
    plus the surname (Guardian style: full name once, then surname)."""
    terms = list(variants)
    if isinstance(last_name, str) and last_name.strip():
        terms += [last_name, plain(last_name)]
    elif variants:
        terms += [variants[0].split()[-1]]
    # the Guardian prints N’Golo / N’Jie with a curly apostrophe, Transfermarkt with ',
    # and sometimes drops it altogether: "Nkoulou", "Njie"
    terms += [t.replace("'", "’") for t in terms] + [t.replace("’", "'") for t in terms]
    for t in list(terms):
        if _has_apostrophe(t):
            words = []
            for w in t.split():
                if _has_apostrophe(w):
                    w = w.replace("'", "").replace("’", "")
                    w = w[0] + w[1:].lower()
                words.append(w)
            terms.append(" ".join(words))
    return _unique(terms)


def _has_apostrophe(text):
    return "'" in text or "’" in text


def name_pattern(terms):
    """Case-sensitive, whole-word regex for any of the terms (longest first)."""
    terms = sorted(terms, key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(t) for t in terms) + r")(?!\w)")


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ\"'‘“])")
FOLLOW_ON = re.compile(r"(?:He|His)\b")


def split_sentences(text):
    text = (text or "").strip()
    return SENT_SPLIT.split(text) if text else []


def player_sentences(sents, pattern):
    """Sentences naming the player, plus the next sentence if it starts with
    He/His (and does not name the player itself). Returns [(sentence, kind)]."""
    named = [bool(pattern.search(s)) for s in sents]
    keep = []
    for i, s in enumerate(sents):
        if named[i]:
            keep.append((s, "named"))
            if i + 1 < len(sents) and not named[i + 1] and FOLLOW_ON.match(sents[i + 1]):
                keep.append((sents[i + 1], "follow-on"))
    return keep


def article_type(tones, api_type=None):
    for tone, label in TONE_TO_TYPE.items():
        if tone in tones:
            return label
    if api_type == "liveblog":
        return "liveblog"
    return "other"


def read_signings():
    need_file(SIGNINGS_CSV, "select")
    s = pd.read_csv(SIGNINGS_CSV, parse_dates=["transfer_date", "date_of_birth"])
    s["name_variants"] = s["name_variants"].fillna("").str.split("|")
    return s


def cache_path(signing_id):
    return CACHE / f"{signing_id}.json"


def cached_version(path):
    """query_version of a cache file (0 if missing/unreadable). Reads only the
    start of the file: query_version is written as the first key."""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(300)
    except OSError:
        return 0
    m = re.search(r'"query_version"\s*:\s*(\d+)', head)
    return int(m.group(1)) if m else 0


# =================================================================== step 1
def select():
    transfers = pd.read_csv(data_file("transfers"))
    players = pd.read_csv(data_file("players"))
    games = pd.read_csv(data_file("games"))
    need_columns(transfers, ["player_id", "transfer_date", "from_club_id", "to_club_id",
                             "from_club_name", "to_club_name", "transfer_fee",
                             "market_value_in_eur"], "transfers")
    need_columns(players, ["player_id", "name", "first_name", "last_name",
                           "date_of_birth", "position"], "players")
    need_columns(games, ["season", "competition_id", "home_club_id", "away_club_id"], "games")

    transfers["transfer_date"] = pd.to_datetime(transfers["transfer_date"], errors="coerce")
    players["date_of_birth"] = pd.to_datetime(players["date_of_birth"], errors="coerce")

    # Loan-return flag, computed on each player's FULL transfer history:
    # the previous move of the same player went to_club -> from_club within 730 days.
    t = (transfers.dropna(subset=["transfer_date"])
         .reset_index().sort_values(["player_id", "transfer_date", "index"]))
    prev = t.groupby("player_id")[["from_club_id", "to_club_id", "transfer_date"]].shift(1)
    t["loan_return"] = ((prev["from_club_id"] == t["to_club_id"])
                        & (prev["to_club_id"] == t["from_club_id"])
                        & ((t["transfer_date"] - prev["transfer_date"]).dt.days <= LOAN_RETURN_DAYS))
    if LOAN_RETURN_KEEP_PAID:
        t["loan_return"] &= ~(t["transfer_fee"] > 0)

    # Which clubs played in the Premier League in which season (from fixtures,
    # so promoted / relegated clubs are handled per season).
    pl = games[games["competition_id"] == PL_COMPETITION_ID]
    pl_set = set(zip(pl["season"], pl["home_club_id"])) | set(zip(pl["season"], pl["away_club_id"]))

    t["season"] = t["transfer_date"].apply(season_of)
    funnel = [("all transfers in the file", len(t))]

    def step(mask, label):
        nonlocal t
        t = t[mask]
        funnel.append((label, len(t)))

    step(t["season"].between(FIRST_SEASON, LAST_SEASON),
         f"seasons {FIRST_SEASON}/{str(FIRST_SEASON + 1)[2:]}-{LAST_SEASON}/{str(LAST_SEASON + 1)[2:]}")
    step(pd.Series([(s, c) in pl_set for s, c in zip(t["season"], t["to_club_id"])], index=t.index),
         "destination in Premier League that season")
    step(t["from_club_id"] != t["to_club_id"], "not same club on both sides")
    step(~t["loan_return"], f"not a loan return (heuristic, {LOAN_RETURN_DAYS} days"
                            + (", paid moves kept)" if LOAN_RETURN_KEEP_PAID else ")"))
    step(t["market_value_in_eur"] >= MIN_MARKET_VALUE_EUR,
         f"market value >= EUR {MIN_MARKET_VALUE_EUR:,}")

    pcols = ["player_id", "name", "first_name", "last_name", "date_of_birth", "position"]
    t = t.merge(players[pcols].drop_duplicates("player_id"), on="player_id", how="left")
    step(t["date_of_birth"].notna() & t["name"].notna(), "player found with name + date of birth")

    t["age_at_transfer"] = completed_years(t["date_of_birth"], t["transfer_date"])
    t["age_group"] = t["age_at_transfer"].apply(age_group)
    lo, hi = AGE_GROUPS[0][1], AGE_GROUPS[-1][2]
    step(t["age_group"].notna(), f"age {lo}-{hi} on transfer date")

    t["signing_id"] = t["player_id"].astype(str) + "_" + t["transfer_date"].dt.strftime("%Y%m%d")
    step(~t["signing_id"].duplicated(), "one row per signing_id")

    t["name_variants"] = ["|".join(name_variants(n, p)) for n, p in zip(t["name"], t["player_id"])]
    t["transfer_date"] = t["transfer_date"].dt.date
    t["date_of_birth"] = t["date_of_birth"].dt.date
    cols = ["signing_id", "player_id", "name", "first_name", "last_name", "name_variants",
            "date_of_birth", "age_at_transfer", "age_group", "position",
            "transfer_date", "season", "from_club_id", "from_club_name",
            "to_club_id", "to_club_name", "transfer_fee", "market_value_in_eur"]
    out = t[cols].sort_values(["transfer_date", "player_id"]).reset_index(drop=True)

    print("Selection funnel:")
    for label, n in funnel:
        print(f"  {n:>7,}  {label}")
    if not save_csv(out, SIGNINGS_CSV, "select"):
        return None
    print(f"\n{len(out)} signings saved to {SIGNINGS_CSV.name}\n")

    labels = [g[0] for g in AGE_GROUPS]
    counts = out.groupby("age_group").size().reindex(labels, fill_value=0)
    print(pd.DataFrame({"signings": counts,
                        "expected (spec)": [f"~{EXPECTED_COUNTS.get(l, '?')}" for l in labels]}).to_string())
    print("\nSignings per season and age group:")
    print(pd.crosstab(out["season"], out["age_group"]).reindex(columns=labels, fill_value=0).to_string())
    return out


# =================================================================== step 2
class StopFetch(Exception):
    """Stop the whole fetch run cleanly (429, bad key, API down)."""


class SkipSigning(Exception):
    """Give up on this one signing (unexpected 4xx); it is retried next run."""


def _api_get(session, params, counter):
    """One API call with the spec's politeness rules. Never prints the key
    (requests error messages contain the URL, so only the error type is shown)."""
    for attempt in range(RETRIES_5XX + 1):
        status = None
        try:
            r = session.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
            status = r.status_code
        except requests.RequestException as e:
            problem = f"network error ({type(e).__name__})"
        counter["calls"] += 1
        time.sleep(PAUSE_SECONDS)

        if status == 200:
            try:
                resp = r.json()["response"]
            except (ValueError, KeyError):
                raise SkipSigning("unreadable response from the API")
            if resp.get("status") != "ok":
                raise SkipSigning(f"API status '{resp.get('status')}': {resp.get('message', '')}")
            return resp
        if status == 429:
            raise StopFetch("HTTP 429: Guardian API limit reached. Cache is kept - "
                            "run fetch again later (e.g. tomorrow) to continue.")
        if status in (401, 403):
            raise StopFetch(f"HTTP {status}: API key missing or invalid "
                            f"(check the {API_KEY_ENV} environment variable).")
        if status is None or status >= 500:
            problem = problem if status is None else f"HTTP {status}"
            if attempt < RETRIES_5XX:
                print(f"    {problem} - retry {attempt + 1}/{RETRIES_5XX} in {RETRY_BACKOFF_SECONDS} s")
                time.sleep(RETRY_BACKOFF_SECONDS)
                continue
            raise StopFetch(f"{problem} after {RETRIES_5XX} retries - the API seems down. "
                            "Cache is kept; run fetch again later.")
        raise SkipSigning(f"HTTP {status}")


NOT_A_CLUB = {"Without Club", "Retired", "Unknown", "Career break"}


def build_query(s):
    """Guardian query for one signing -> (query, filter_by_name).

    Normal names: '"v1" OR "v2" ...'. The Guardian search cannot handle names
    with an apostrophe (a curly ’ is a syntax error, a straight ' hardly matches;
    tested 7 Nov 2026), so for those:
      - apostrophe only in the first name (N'Golo Kanté): search the surname
      - apostrophe in the surname (Dara O'Shea): the surname without apostrophe
        (the Guardian writes 'Njie') OR (first name AND (old club OR new club))
    These broader queries return extra articles, so build() keeps only articles
    that actually name the player (filter_by_name=True)."""
    variants = s["name_variants"] or [s["name"]]
    if not any(_has_apostrophe(v) for v in variants):
        return " OR ".join(f'"{v}"' for v in variants), False
    parts = [f'"{v}"' for v in variants if not _has_apostrophe(v)]
    last = s["last_name"] if isinstance(s["last_name"], str) else variants[0].split()[-1]
    first = s["first_name"] if isinstance(s["first_name"], str) else variants[0].split()[0]
    if not _has_apostrophe(last):
        parts += [f'"{last}"', f'"{plain(last)}"']
    else:
        parts.append(f'"{last.replace(chr(39), "").replace("’", "")}"')
        clubs = []
        for c in (s["from_club_name"], s["to_club_name"]):
            if isinstance(c, str) and c not in NOT_A_CLUB:
                w = c.split()[-1]
                if not _has_apostrophe(w) and w not in clubs:
                    clubs.append(w)
        if clubs and not _has_apostrophe(first):
            parts.append(f'({first} AND ({" OR ".join(clubs)}))')
    out = []
    for p in parts:
        if p not in out:
            out.append(p)
    return " OR ".join(out), True


def fetch_signing(session, s, key, counter):
    """All pages of the Guardian query for one signing -> cache dict."""
    query, filter_by_name = build_query(s)
    start = s["transfer_date"] - pd.Timedelta(days=WINDOW_DAYS)
    end = s["transfer_date"] + pd.Timedelta(days=WINDOW_DAYS)
    params = {
        "q": query, "section": "football",
        "from-date": start.strftime("%Y-%m-%d"), "to-date": end.strftime("%Y-%m-%d"),
        "show-fields": SHOW_FIELDS, "show-tags": SHOW_TAGS,
        "page-size": PAGE_SIZE, "order-by": "oldest", "api-key": key,
    }
    articles, page, pages = [], 1, 1
    while page <= pages:
        resp = _api_get(session, {**params, "page": page}, counter)
        articles += resp.get("results", [])
        pages = int(resp.get("pages", 1) or 1)
        page += 1
    return {   # query_version first: cached_version() reads only the file start
        "query_version": QUERY_VERSION,
        "signing_id": s["signing_id"], "name": s["name"], "query": query,
        "filter_by_name": filter_by_name,
        "window_from": params["from-date"], "window_to": params["to-date"],
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages": pages, "n_articles": len(articles),
        "articles": articles,
    }


def fetch(limit=None):
    """Fetch every signing that is not cached yet (at most `limit` signings)."""
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        print(f"API key missing or invalid: set the {API_KEY_ENV} environment variable first.")
        return None
    signings = read_signings()
    CACHE.mkdir(exist_ok=True)

    todo = [s for _, s in signings.iterrows()
            if cached_version(cache_path(s["signing_id"])) < QUERY_VERSION]
    print(f"{len(signings)} signings: {len(signings) - len(todo)} already cached, "
          f"{len(todo)} to fetch" + (f" (this run: at most {limit})" if limit else ""))
    if limit:
        todo = todo[:int(limit)]

    counter = {"calls": 0}
    fetched, skipped, stop_message = 0, [], None
    with requests.Session() as session:
        for i, s in enumerate(todo, 1):
            calls_before = counter["calls"]
            try:
                d = fetch_signing(session, s, key, counter)
            except StopFetch as e:
                stop_message = str(e)
                break
            except SkipSigning as e:
                skipped.append(s["signing_id"])
                print(f"[{i}/{len(todo)}] {s['signing_id']:<18} {s['name'][:28]:<28} SKIPPED ({e})")
                continue
            out = cache_path(s["signing_id"])
            tmp = out.with_suffix(".json.tmp")          # write-then-rename: no half files
            tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, out)
            fetched += 1
            print(f"[{i}/{len(todo)}] {s['signing_id']:<18} {s['name'][:28]:<28} "
                  f"{d['n_articles']:>5} articles  {counter['calls'] - calls_before} call(s)")

    remaining = sum(cached_version(cache_path(sid)) < QUERY_VERSION for sid in signings["signing_id"])
    print("\n" + (f"STOPPED: {stop_message}\n" if stop_message else "")
          + f"Signings fetched this run: {fetched}\n"
          f"API calls made this run:   {counter['calls']}\n"
          f"Skipped (error, retried next run): {len(skipped)}\n"
          f"Signings still to fetch:   {remaining} of {len(signings)}")
    return {"fetched": fetched, "calls": counter["calls"], "skipped": skipped,
            "remaining": remaining, "stopped": stop_message}


# =================================================================== step 3
ARTICLE_COLS = ["article_id", "url", "publication_date", "headline", "byline", "wordcount",
                "tones", "keywords", "article_type", "body_text"]
SENTENCE_COLS = ["article_id", "signing_id", "player", "period", "days_from_transfer",
                 "age_at_article", "age_group_at_transfer", "article_type", "match_kind", "sentence"]
LINK_COLS = ["article_id", "signing_id", "player_id", "player", "publication_date",
             "days_from_transfer", "period", "age_at_article", "age_group_at_transfer",
             "mentions", "total_sentences", "share_of_sentences", "name_in_headline",
             "is_focus_article", "player_sentences", "article_type", "overlapping_window"]
CHUNK_ROWS = 2000           # rows held in memory before they are written to disk


class _ChunkWriter:
    """Collects rows and appends them to a file every CHUNK_ROWS rows, so build()
    never holds all article texts or sentences in memory at once.
    kind='parquet' needs pyarrow; kind='csv' always works."""

    def __init__(self, path, cols, kind="csv"):
        self.path, self.cols, self.kind = path, cols, kind
        self.rows, self.n, self._pq = [], 0, None
        if path.exists():
            path.unlink()

    def add(self, row):
        self.rows.append(row)
        if len(self.rows) >= CHUNK_ROWS:
            self.flush()

    def flush(self):
        if not self.rows:
            return
        df = pd.DataFrame(self.rows, columns=self.cols)
        self.rows = []
        if self.kind == "parquet":
            import pyarrow as pa
            import pyarrow.parquet as pq
            schema = pa.schema([("article_id", pa.string()), ("url", pa.string()),
                                ("publication_date", pa.timestamp("ns")), ("headline", pa.string()),
                                ("byline", pa.string()), ("wordcount", pa.float64()),
                                ("tones", pa.string()), ("keywords", pa.string()),
                                ("article_type", pa.string()), ("body_text", pa.string())])
            table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
            if self._pq is None:
                self._pq = pq.ParquetWriter(str(self.path), schema)
            self._pq.write_table(table)
        else:
            df.to_csv(self.path, mode="a", index=False, header=self.n == 0, encoding="utf-8-sig"
                      if self.n == 0 else "utf-8")
        self.n += len(df)

    def close(self):
        self.flush()
        if self._pq is not None:
            self._pq.close()


def _locked(paths):
    """Output files that are open in another program (Excel locks files on Windows)."""
    out = []
    for p in paths:
        if p.exists():
            try:
                with open(p, "a"):
                    pass
            except PermissionError:
                out.append(p)
    return out


def build():
    signings = read_signings().set_index("signing_id")
    need_file(CACHE, "fetch")
    files = sorted(CACHE.glob("*.json"))
    if not files:
        raise PipelineError(f"{CACHE.name}/ is empty - run 'fetch' first.")

    try:
        import pyarrow  # noqa: F401
        art_path, art_kind = ARTICLES_PARQUET, "parquet"
    except ImportError:
        print(f"pyarrow not installed - writing {ARTICLES_CSV.name} instead of {ARTICLES_PARQUET.name}.")
        art_path, art_kind = ARTICLES_CSV, "csv"
    locked = _locked([art_path, ARTICLE_PLAYER_CSV, SENTENCES_CSV])
    if locked:
        for p in locked:
            print(f"!! Could not write {p.name} (it is open in another program): "
                  f"close {p.name} in Excel and re-run build.")
        return None

    # all selected signings per player: needed for overlapping_window
    tdates_by_player = signings.groupby("player_id")["transfer_date"].apply(list).to_dict()

    art_tmp = art_path.with_name(art_path.name + ".tmp")
    sent_raw = SENTENCES_CSV.with_name(SENTENCES_CSV.name + ".raw.tmp")
    art_out = _ChunkWriter(art_tmp, ARTICLE_COLS, art_kind)
    sent_out = _ChunkWriter(sent_raw, SENTENCE_COLS, "csv")
    seen_articles, type_counts = set(), {}
    links = []               # one tuple per (article, signing), LINK_COLS order
    n_old, n_unknown, n_read = 0, 0, 0

    for i, f in enumerate(files, 1):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print(f"  skipping unreadable cache file {f.name}")
            continue
        if d.get("query_version", 0) < QUERY_VERSION:
            n_old += 1
            continue
        sid = d["signing_id"]
        if sid not in signings.index:
            n_unknown += 1
            continue
        n_read += 1
        s = signings.loc[sid]
        pattern = name_pattern(match_terms(s["name_variants"], s["last_name"]))
        tdate, dob = s["transfer_date"], s["date_of_birth"]
        others = [t for t in tdates_by_player[s["player_id"]] if t != tdate]

        for a in d.get("articles", []):
            aid = a.get("id")
            if not aid:
                continue
            fields = a.get("fields", {}) or {}
            body = fields.get("bodyText", "") or ""
            headline = fields.get("headline") or a.get("webTitle", "") or ""
            if d.get("filter_by_name") and not (pattern.search(headline) or pattern.search(body)):
                continue        # broad query (apostrophe name): keep only articles naming him
            tags = a.get("tags", []) or []
            tones = [t["id"] for t in tags if t.get("type") == "tone"]
            atype = article_type(tones, a.get("type"))
            pub = pd.Timestamp(a["webPublicationDate"]).tz_convert(None)

            if aid not in seen_articles:
                seen_articles.add(aid)
                type_counts[atype] = type_counts.get(atype, 0) + 1
                art_out.add([aid, a.get("webUrl", ""), pub, headline, fields.get("byline", ""),
                             pd.to_numeric(fields.get("wordcount"), errors="coerce"),
                             ";".join(tones),
                             ";".join(t["id"] for t in tags if t.get("type") == "keyword"),
                             atype, body])

            sents = split_sentences(body)
            kept = player_sentences(sents, pattern)
            mentions = sum(k == "named" for _, k in kept)
            share = mentions / len(sents) if sents else 0.0
            in_headline = bool(pattern.search(headline))
            pub_day = pub.normalize()
            days = (pub_day - tdate).days
            period = ("before" if days < -AROUND_DAYS else
                      "after" if days > AROUND_DAYS else "around")
            age_at = round((pub_day - dob).days / 365.25, 2)

            links.append((aid, sid, s["player_id"], s["name"], pub_day.date(), days, period,
                           age_at, s["age_group"], mentions, len(sents), round(share, 4),
                           in_headline, in_headline or share >= FOCUS_SHARE,
                           " ".join(x for x, _ in kept), atype,
                           any(abs((pub_day - t).days) <= WINDOW_DAYS for t in others)))
            for sentence, kind in kept:
                sent_out.add([aid, sid, s["name"], period, days, age_at, s["age_group"],
                              atype, kind, sentence])
        del d
        if i % 100 == 0:
            print(f"  {i}/{len(files)} cache files read ({len(seen_articles):,} unique articles)")

    art_out.close()
    sent_out.close()
    if n_old or n_unknown:
        print(f"Ignored {n_old} cache files with an old query_version and "
              f"{n_unknown} for signings not in {SIGNINGS_CSV.name}.")
    if not links:
        print("No articles in the cache yet - nothing to build.")
        for p in (art_tmp, sent_raw):
            p.unlink(missing_ok=True)
        return None

    ap = pd.DataFrame(links, columns=LINK_COLS).drop_duplicates(["article_id", "signing_id"])
    del links
    n_links_raw = len(ap)

    # n_tracked_players_in_article: other tracked PLAYERS whose query found this article
    players_per_article = ap.groupby("article_id")["player_id"].nunique()
    ap["n_tracked_players_in_article"] = ap["article_id"].map(players_per_article) - 1

    # dedup rule: one article, several signings of the SAME player
    # -> keep the transfer with the smallest |days_from_transfer| (tie: earlier transfer)
    ap["_abs"] = ap["days_from_transfer"].abs()
    ap = (ap.sort_values(["article_id", "player_id", "_abs", "days_from_transfer"],
                         ascending=[True, True, True, False])
            .drop_duplicates(["article_id", "player_id"]).drop(columns="_abs"))
    n_dedup = n_links_raw - len(ap)

    # mixed_age_article: tracked players from both the young and the old group
    young, old = AGE_GROUPS[0][0], AGE_GROUPS[-1][0]
    groups = ap.groupby("article_id")["age_group_at_transfer"].agg(set)
    mixed = groups.apply(lambda g: young in g and old in g)
    ap["mixed_age_article"] = ap["article_id"].map(mixed)

    ap_cols = ["article_id", "signing_id", "player_id", "player", "publication_date",
               "days_from_transfer", "period", "age_at_article", "age_group_at_transfer",
               "mentions", "total_sentences", "share_of_sentences", "name_in_headline",
               "n_tracked_players_in_article", "is_focus_article",
               "player_sentences", "article_type", "overlapping_window", "mixed_age_article"]
    ap = ap[ap_cols].sort_values(["signing_id", "publication_date", "article_id"]).reset_index(drop=True)

    # sentences only for the links that survived the dedup rule (filtered chunk by chunk)
    keep = set(zip(ap["article_id"], ap["signing_id"]))
    sent_tmp = SENTENCES_CSV.with_name(SENTENCES_CSV.name + ".tmp")
    sent_tmp.unlink(missing_ok=True)
    n_sent, first = 0, True
    if sent_raw.exists():
        for chunk in pd.read_csv(sent_raw, chunksize=50_000):
            mask = [(a, b) in keep for a, b in zip(chunk["article_id"], chunk["signing_id"])]
            chunk = chunk[mask]
            chunk.to_csv(sent_tmp, mode="a", index=False, header=first,
                         encoding="utf-8-sig" if first else "utf-8")
            n_sent += len(chunk)
            first = False
        sent_raw.unlink()
    if first:                                   # no sentences at all: header only
        pd.DataFrame(columns=SENTENCE_COLS).to_csv(sent_tmp, index=False, encoding="utf-8-sig")

    ap_tmp = ARTICLE_PLAYER_CSV.with_name(ARTICLE_PLAYER_CSV.name + ".tmp")
    ap.to_csv(ap_tmp, index=False, encoding="utf-8-sig")

    written, failed = [], []
    for tmp, final in [(art_tmp, art_path), (ap_tmp, ARTICLE_PLAYER_CSV), (sent_tmp, SENTENCES_CSV)]:
        try:
            os.replace(tmp, final)
            written.append(final.name)
        except PermissionError:
            failed.append(final.name)
            print(f"!! Could not write {final.name} (it is open in another program): "
                  f"close {final.name} in Excel and re-run build.")

    print(f"\nCache files read:   {n_read}")
    print(f"Unique articles:    {len(seen_articles):,}")
    print(f"Article-signing links: {len(ap):,}  "
          f"({n_dedup} dropped by the same-player dedup rule)")
    print(f"Sentences:          {n_sent:,}")
    print(f"Focus links:        {int(ap['is_focus_article'].sum()):,} "
          f"({ap['is_focus_article'].mean():.0%})")
    print("\nLinks per period:")
    print(ap["period"].value_counts().reindex(["before", "around", "after"], fill_value=0).to_string())
    print("\nArticle types (unique articles):")
    print(pd.Series(type_counts).sort_values(ascending=False).to_string())
    print(f"\nFlags: liveblog {(ap.article_type == 'liveblog').sum()}, "
          f"overlapping_window {int(ap.overlapping_window.sum())}, "
          f"mixed_age_article {int(ap.mixed_age_article.sum())} links")
    print("\nWritten: " + ", ".join(written))
    if failed:
        print("Some files were NOT written - see the messages above.")
    return ap


# =================================================================== step 4
def _table(title, df):
    print(f"\n--- {title}")
    print(df.to_string() if len(df) else "(none)")


def validate():
    signings = read_signings()
    need_file(ARTICLE_PLAYER_CSV, "build")
    ap = pd.read_csv(ARTICLE_PLAYER_CSV)
    labels = [g[0] for g in AGE_GROUPS]

    # --- integrity
    dup_links = ap.duplicated(["article_id", "signing_id"]).sum()
    dup_player = ap.duplicated(["article_id", "player_id"]).sum()
    print(f"Integrity: duplicate (article, signing) keys: {dup_links}; "
          f"article linked twice to the same player: {dup_player}")

    fetched = signings["signing_id"].map(lambda sid: cached_version(cache_path(sid)) >= QUERY_VERSION)
    print(f"Signings fetched: {int(fetched.sum())} of {len(signings)}"
          + ("" if fetched.all() else "  (validate covers fetched signings only)"))
    sg = signings[fetched].copy()

    per = ap.groupby(["signing_id", "period"]).size().unstack(fill_value=0)
    per = per.reindex(columns=["before", "around", "after"], fill_value=0)
    per["total"] = per.sum(axis=1)
    per["focus"] = ap[ap.is_focus_article].groupby("signing_id").size()
    sg = sg.join(per, on="signing_id")
    for c in ["before", "around", "after", "total", "focus"]:
        sg[c] = sg[c].fillna(0).astype(int)

    # --- 1. signings with 0 articles
    zero = sg[sg.total == 0][["signing_id", "name", "age_group", "season", "to_club_name",
                              "market_value_in_eur"]].copy()
    zero["query_names"] = sg.loc[zero.index, "name_variants"].str.join(" | ")
    _table(f"Signings with 0 articles: {len(zero)} "
           f"(check spelling, add ALIASES, delete cache file, re-fetch)", zero.head(40))
    if len(zero) > 40:
        print(f"... {len(zero) - 40} more")
    if len(zero):
        save_csv(zero, ZERO_ARTICLES_CSV, "validate")
        print(f"Full list in {ZERO_ARTICLES_CSV.name}")

    # --- 2. articles per signing by age group and period
    def describe(x):
        return pd.Series({"signings": len(x), "median": x.median(), "q25": x.quantile(.25),
                          "q75": x.quantile(.75), "max": x.max(), "zero": (x == 0).sum()})
    dist = sg.groupby("age_group")["total"].apply(describe).unstack().reindex(labels)
    _table("Articles per signing (all links), by age group", dist)
    med = sg.groupby("age_group")[["before", "around", "after", "focus"]].median().reindex(labels)
    _table("Median articles per signing, by age group and period (+ focus articles)", med)

    # --- 3. before vs after balance
    k = MIN_ARTICLES_PER_PERIOD
    fb = ap[ap.is_focus_article].groupby(["signing_id", "period"]).size().unstack(fill_value=0)
    fb = fb.reindex(columns=["before", "after"], fill_value=0)
    sg["focus_balanced"] = sg["signing_id"].map((fb["before"] >= k) & (fb["after"] >= k)).eq(True)
    sg["balanced"] = (sg.before >= k) & (sg.after >= k)
    bal = sg.groupby("age_group").agg(signings=("signing_id", "size"),
                                      both_periods=("balanced", "mean"),
                                      both_periods_focus_only=("focus_balanced", "mean")).reindex(labels)
    bal[["both_periods", "both_periods_focus_only"]] = (
        bal[["both_periods", "both_periods_focus_only"]] * 100).round(1)
    _table(f"Before/after balance: % of signings with >= {k} articles in BOTH before and after", bal)

    # --- 4. coverage bias young vs old
    sg["mv_band"] = pd.cut(sg.market_value_in_eur, [0, 5e6, 15e6, 40e6, float("inf")],
                           labels=["2-5m", "5-15m", "15-40m", "40m+"], right=False)
    cov = sg.pivot_table(index="mv_band", columns="age_group", values="total",
                         aggfunc="median", observed=False).reindex(columns=labels)
    _table("Coverage bias: median articles per signing by market value band x age group", cov)
    y, o = labels[0], labels[-1]
    my, mo = sg.loc[sg.age_group == y, "total"].median(), sg.loc[sg.age_group == o, "total"].median()
    print(f"Median articles per signing: {y} {my}, {o} {mo}"
          + (f"  (ratio {y}/{o} = {my / mo:.2f})" if mo else ""))

    # --- 5. time spread: links per transfer season and age group
    ap2 = ap.merge(signings[["signing_id", "season"]], on="signing_id", how="left")
    _table("Time spread: article links per transfer season and age group",
           pd.crosstab(ap2.season, ap2.age_group_at_transfer).reindex(columns=labels, fill_value=0))

    # --- 6. default exclusions (flags are kept in the data)
    excl = pd.DataFrame({
        "links": [len(ap)],
        "liveblog": [(ap.article_type == "liveblog").sum()],
        "mixed_age_article": [ap.mixed_age_article.sum()],
        "overlapping_window": [ap.overlapping_window.sum()],
        "left after all three": [(~((ap.article_type == "liveblog") | ap.mixed_age_article
                                    | ap.overlapping_window)).sum()],
    })
    _table("Default exclusions (counts of links)", excl)
    _table("Article types (links)", ap.article_type.value_counts().to_frame("links"))

    # --- 7. focus check sample for hand-reading
    n = min(FOCUS_SAMPLE_SIZE, len(ap))
    sample = ap.sample(n=n, random_state=RANDOM_SEED)
    art_path = ARTICLES_PARQUET if ARTICLES_PARQUET.exists() else ARTICLES_CSV
    if art_path.exists():
        art = (pd.read_parquet(art_path, columns=["article_id", "headline", "url"])
               if art_path.suffix == ".parquet"
               else pd.read_csv(art_path, usecols=["article_id", "headline", "url"]))
        sample = sample.merge(art, on="article_id", how="left")
    sample = sample[[c for c in ["signing_id", "player", "article_id", "url", "headline",
                                 "period", "article_type", "mentions", "share_of_sentences",
                                 "name_in_headline", "is_focus_article", "player_sentences"]
                     if c in sample.columns]]
    sample["truly_about_player (y/n)"] = ""
    if save_csv(sample, FOCUS_SAMPLE_CSV, "validate"):
        print(f"\nFocus check: {n} random article_player rows written to {FOCUS_SAMPLE_CSV.name} "
              f"(fill in the last column; {int(sample.is_focus_article.sum())} of them are focus articles).")
    return sg


# =================================================================== command line
STEPS = {"select": select, "fetch": fetch, "build": build, "validate": validate}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in STEPS:
        sys.exit("Usage: python get_guardian_articles.py select|fetch [N]|build|validate")
    try:
        args = sys.argv[2:3] if sys.argv[1] == "fetch" else []
        STEPS[sys.argv[1]](*args)
    except PipelineError as e:
        sys.exit(f"ERROR: {e}")
