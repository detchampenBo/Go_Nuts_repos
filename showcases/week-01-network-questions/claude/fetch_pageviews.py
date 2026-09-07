"""Fetch Jun-Aug 2026 Wikipedia pageviews for the 303 week-1 characters.

Two Wikimedia sources, merged:
  1. MediaWiki action=query&prop=pageviews  (batched, fast, but omits many pages)
  2. REST .../per-article/.../monthly/2026060100/2026083100  (fills the gaps)

Output: assets/pageviews.json  -- one row per node_id with name, views, degrees.
Run:  ../../../.venv/bin/python fetch_pageviews.py
"""
import csv, json, os, sys, time, random, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / ".." / ".." / ".." / "data" / "week1"
OUT = HERE / "assets" / "pageviews.json"
UA = "socialgraphs2026-gonuts/1.0 (DTU 02805 course exercise; contact via github)"
MW = "https://en.wikipedia.org/w/api.php?"
REST = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        "en.wikipedia/all-access/user/{}/monthly/2026060100/2026083100")


def rows(p):
    with open(p, encoding="utf-8") as fh:
        yield from csv.reader((l for l in fh if not l.startswith("#")), delimiter="\t")


def get(url, tries=8):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            w = min(60, 6 * (a + 1)) + random.random() * 3
            print(f"  HTTP {e.code}; sleep {w:.0f}s", flush=True)
            time.sleep(w)
        except Exception as e:  # noqa: BLE001
            print("  ", e, flush=True)
            time.sleep(5)
    return None


def main():
    nrows = list(rows(DATA / "week1_nodes.tsv"))
    H = nrows[0]
    meta = {r[0]: dict(zip(H, r)) for r in nrows[1:]}
    ids = list(meta)

    ind = {n: 0 for n in ids}
    outd = {n: 0 for n in ids}
    for a, b in rows(DATA / "week1_edges.tsv"):
        if a == "source":
            continue
        outd[a] += 1
        ind[b] += 1

    ckpt = HERE / "assets" / "_pageviews_partial.json"
    views = ({k: tuple(v) for k, v in json.load(open(ckpt)).items()}
             if ckpt.exists() else {})

    def save_ckpt():
        ckpt.write_text(json.dumps({k: list(v) for k, v in views.items()}))

    # -- pass 1: batched MediaWiki prop=pageviews (rolling ~60d, used only to seed) --
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        q = urllib.parse.urlencode({
            "action": "query", "prop": "pageviews", "format": "json",
            "formatversion": "2", "redirects": "1",
            "titles": "|".join(x.replace("_", " ") for x in batch)})
        d = get(MW + q)
        if not d or "query" not in d:
            continue
        qy = d["query"]
        back = {}
        for r in qy.get("normalized", []):
            back[r["to"]] = r["from"]
        for r in qy.get("redirects", []):
            back[r["to"]] = back.get(r["from"], r["from"])
        for p in qy["pages"]:
            src = back.get(p["title"], p["title"]).replace(" ", "_")
            vv = [v for v in (p.get("pageviews") or {}).values() if v]
            if vv and src in meta and src not in views:
                views[src] = ("mediawiki_rolling60d", sum(vv))
        save_ckpt()
        time.sleep(2.5)
    print(f"pass 1 (MediaWiki): {len(views)}/{len(ids)}", flush=True)

    # -- pass 2: REST monthly Jun+Jul+Aug 2026, authoritative; overwrites pass 1 --
    REST_SRC = "rest_monthly_2026-06_to_2026-08"
    todo = [n for n in ids if views.get(n, ("",))[0] not in (REST_SRC, "none")]
    print(f"pass 2 (REST): {len(ids) - len(todo)} done, {len(todo)} to go", flush=True)
    for k, nid in enumerate(todo):
        d = get(REST.format(urllib.parse.quote(nid, safe="")), tries=10)
        if d and d.get("items"):
            views[nid] = (REST_SRC, sum(x["views"] for x in d["items"]))
        elif nid not in views:
            views[nid] = ("none", 0)
        time.sleep(2.2)
        if k % 15 == 14:
            save_ckpt()
            print(f"pass 2 (REST): {k + 1}/{len(todo)}", flush=True)
    save_ckpt()

    out = [{
        "node_id": n,
        "name": meta[n]["name"],
        "views": views[n][1],
        "views_source": views[n][0],
        "in_degree": ind[n],
        "out_degree": outd[n],
    } for n in ids]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "window": "2026-06-01 .. 2026-08-31 (monthly, all-access, user agent)",
        "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n": len(out),
        "rows": out,
    }, indent=2) + "\n", encoding="utf-8")

    have = [r for r in out if r["views"] > 0]
    print(f"\nwrote {OUT.relative_to(HERE)}  ({len(have)}/{len(out)} with views > 0)")

    # -- Spearman rho, views vs in-degree (no scipy dependency) --
    def spearman(x, y):
        def rank(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            rk = [0.0] * len(v)
            i = 0
            while i < len(v):
                j = i
                while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                    j += 1
                avg = (i + j) / 2 + 1
                for t in range(i, j + 1):
                    rk[order[t]] = avg
                i = j + 1
            return rk
        rx, ry = rank(x), rank(y)
        n = len(x)
        mx, my = sum(rx) / n, sum(ry) / n
        cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
        sx = sum((a - mx) ** 2 for a in rx) ** 0.5
        sy = sum((b - my) ** 2 for b in ry) ** 0.5
        return cov / (sx * sy)

    xs = [r["views"] for r in out]
    yi = [r["in_degree"] for r in out]
    yo = [r["out_degree"] for r in out]
    print(f"\nSpearman rho  (n={len(out)}, all 303):")
    print(f"  views vs in-degree : {spearman(xs, yi):+.3f}")
    print(f"  views vs out-degree: {spearman(xs, yo):+.3f}")
    hv = [r for r in out if r["views"] > 0]
    print(f"  views vs in-degree (views>0, n={len(hv)}): "
          f"{spearman([r['views'] for r in hv], [r['in_degree'] for r in hv]):+.3f}")

    print("\nread FAR more than linked (top residual, views-rank minus in-rank):")
    rv = {r['node_id']: i for i, r in enumerate(sorted(out, key=lambda r: -r['views']))}
    ri = {r['node_id']: i for i, r in enumerate(sorted(out, key=lambda r: -r['in_degree']))}
    for r in sorted(out, key=lambda r: ri[r['node_id']] - rv[r['node_id']], reverse=True)[:8]:
        print(f"  {r['name']:28} {r['views']:9,} views   in {r['in_degree']:3}")
    print("linked FAR more than read:")
    for r in sorted(out, key=lambda r: rv[r['node_id']] - ri[r['node_id']], reverse=True)[:8]:
        print(f"  {r['name']:28} {r['views']:9,} views   in {r['in_degree']:3}")


if __name__ == "__main__":
    main()
