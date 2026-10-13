"""Zambia: list and download Acts from the National Assembly of Zambia website
(https://www.parliament.gov.zm).

Two collections:
  * "Laws of Zambia" revised edition, Volumes 1-26 (+ "Acts of Parliament (Post 1997)"),
    one node page (and one PDF) per Chapter:   /acts/volumes -> /acts/volume/<id> -> /node/<n>
  * Acts of Parliament as enacted, by year:     /acts-of-parliament?page=N -> /node/<n>

robots.txt asks for Crawl-delay: 10, which is obeyed (one request every 10 s, no parallelism).
Everything is cached in _raw/zm/ so the script can be re-run/resumed.

Usage: python zm_fetch.py [list|pdfs|all]
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zm_text import fetch, pdf_ok  # noqa: E402

BASE = "https://www.parliament.gov.zm"
RAW = os.environ.get("ZM_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "zm"))
DELAY = 10.0
# The server does not send its intermediate certificate (RapidSSL TLS RSA CA G1); build a CA bundle
# = certifi + that intermediate (fetched from the AIA URL in the site certificate).
INTERMEDIATE = "http://cacerts.rapidssl.com/RapidSSLTLSRSACAG1.crt"


def ca_bundle():
    import subprocess
    import certifi
    import requests
    pem = os.path.join(RAW, "ca-bundle.pem")
    if not os.path.exists(pem):
        der = requests.get(INTERMEDIATE, timeout=60).content
        inter = subprocess.run(["openssl", "x509", "-inform", "der"], input=der, capture_output=True).stdout
        with open(pem, "wb") as f:
            f.write(open(certifi.where(), "rb").read() + b"\n" + inter)
    return pem


VERIFY = None


def get(path, name):
    dest = os.path.join(RAW, "html", name)
    p = fetch(BASE + path, dest, delay=DELAY, verify=VERIFY)
    return open(p, encoding="utf-8", errors="replace").read() if p else ""


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def nodes_in(h):
    i = h.find("view-content")
    j = h.find("rightbar-content")
    return h[i:j] if i >= 0 else ""


def list_all():
    items = {}
    # revised edition volumes
    vh = get("/acts/volumes", "volumes.html")
    vols = re.findall(r"href='/acts/volume/(\d+)'>([^<]+)</a>", vh)
    for vid, vname in vols:
        h = get("/acts/volume/%s" % vid, "volume-%s.html" % vid)
        for n, t in re.findall(r'href="/node/(\d+)">(.*?)</a>', nodes_in(h), re.S):
            items.setdefault(n, {"node": n, "title": text(t), "collection": "volume", "volume": vname.strip()})
    # acts listing
    h0 = get("/acts-of-parliament", "acts-0.html")
    last = max([int(x) for x in re.findall(r"acts-of-parliament\?page=(\d+)", h0)] or [0])
    for pg in range(0, last + 1):
        h = h0 if pg == 0 else get("/acts-of-parliament?page=%d" % pg, "acts-%d.html" % pg)
        body = nodes_in(h)
        year = None
        for m in re.finditer(r"<h3>(.*?)</h3>|href=\"/node/(\d+)\">(.*?)</a>", body, re.S):
            if m.group(1) is not None:
                year = text(m.group(1))
                continue
            n, raw = m.group(2), m.group(3)
            num = re.search(r"Act No\.\s*([\w./-]*)\s*of\s*(\d{4})?", text(raw))
            title = text(re.sub(r"<div class='act-number-appended'>.*?</div>", "", raw, flags=re.S))
            it = {"node": n, "title": title, "collection": "acts", "list_year": year,
                  "act_no": (num.group(1) if num else "") or "", "act_year": (num.group(2) if num else "") or ""}
            if n in items:
                items[n].update({k: v for k, v in it.items() if k not in ("collection",)})
                items[n]["also_in_acts_list"] = True
            else:
                items[n] = it
    # constitution amendment act 2016 (menu link)
    items.setdefault("4834", {"node": "4834", "title": "Constitution of Zambia (Amendment) Act, 2016", "collection": "constitution"})
    json.dump(items, open(os.path.join(RAW, "index.json"), "w"), indent=1)
    print("listed", len(items))
    return items


def node_details(items):
    for k, it in sorted(items.items(), key=lambda kv: int(kv[0])):
        if "pdfs" in it:
            continue
        h = get("/node/%s" % k, "node-%s.html" % k)
        body = h[h.find("<h1"):h.find("rightbar-content")]
        pdfs = [html.unescape(u) for u in re.findall(r'href="([^"]+\.pdf)"', body, re.I)]
        pdfs = [u if u.startswith("http") else BASE + u for u in pdfs]
        it["pdfs"] = list(dict.fromkeys(pdfs))
        m = re.search(r'<div class="field-item even"[^>]*>(.*?)</div>', body, re.S)
        it["summary"] = text(m.group(1)) if m else ""
        m = re.search(r"Volume:&nbsp;</div>\s*<div[^>]*>\s*<div[^>]*>(.*?)</div>", body, re.S)
        if m:
            it["volume"] = text(m.group(1))
        json.dump(items, open(os.path.join(RAW, "index.json"), "w"), indent=1)


def download(items):
    for k, it in sorted(items.items(), key=lambda kv: int(kv[0])):
        for i, u in enumerate(it.get("pdfs", [])):
            dest = os.path.join(RAW, "pdf", "%s-%d.pdf" % (k, i))
            if os.path.exists(dest) and pdf_ok(dest):
                continue
            r = fetch(u, dest, delay=DELAY, check_pdf=True, timeout=300, verify=VERIFY)
            if not r:
                print("FAILED", k, u)


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    VERIFY = ca_bundle()
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    idx = os.path.join(RAW, "index.json")
    items = json.load(open(idx)) if os.path.exists(idx) and what == "pdfs" else None
    if items is None:
        items = list_all()
        node_details(items)
    download(items)
