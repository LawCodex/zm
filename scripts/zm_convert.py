"""Zambia: convert the National Assembly PDFs to Markdown.
Usage: python zm_convert.py <repo_dir>

* "volume" items (Laws of Zambia, revised edition, Volumes 1-26 and "Acts of Parliament (Post 1997)"):
  laws-of-zambia/cap-<chapter>-<slug>.md (chapter number read from the PDF text when printed);
* "acts" items (Acts of Parliament as enacted, by year): acts/<year>/act-<no>-<slug>.md;
* the Constitution of Zambia (Amendment) Act, 2016: constitution/.
PDFs without a usable text layer (scans) are skipped (no OCR)."""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zm_text import pdf_text, clean_pages, structure, write_md, slug, text_quality, pdf_ok  # noqa: E402

RAW = os.environ.get("ZM_RAW", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "zm"))
TODAY = datetime.date.today().isoformat()


def clean_title(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^The\s+", "The ", t)
    return t


def main(repo):
    items = json.load(open(os.path.join(RAW, "index.json")))
    n = skipped = missing = 0
    seen = set()
    for k, it in sorted(items.items(), key=lambda kv: int(kv[0])):
        pdfs = it.get("pdfs") or []
        if not pdfs:
            continue
        f = os.path.join(RAW, "pdf", "%s-0.pdf" % k)
        if not os.path.exists(f) or not pdf_ok(f):
            missing += 1
            continue
        pages, _ = pdf_text(f)
        full = "\n".join(pages)
        if len(re.sub(r"\s", "", full)) < 500 or text_quality(full) < 0.7:
            print("SKIP (no usable text layer)", k, it["title"])
            skipped += 1
            continue
        title = clean_title(it["title"])
        head = "\n".join(full.splitlines()[:80])
        if it["collection"] == "constitution":
            path = os.path.join(repo, "constitution", "constitution-of-zambia-amendment-act-2016.md")
            meta = {"title": "Constitution of Zambia (Amendment) Act, 2016", "identifier": "Act No. 2 of 2016",
                    "type": "constitution", "year": "2016"}
            title = meta["title"]
        elif it["collection"] == "volume" and not it.get("act_no"):
            cap = re.search(r"\bCHAPTER\s+(\d{1,3}[A-Z]?)\b", head) or re.search(r"\bCAP(?:\.|ITLE)?\s+(\d{1,3}[A-Z]?)\b", head)
            capn = cap.group(1) if cap else ""
            name = ("cap-%s-" % capn if capn else "") + slug(title)[:80]
            path = os.path.join(repo, "laws-of-zambia", name + ".md")
            meta = {"title": title, "identifier": ("Cap. " + capn) if capn else "", "type": "act",
                    "volume": it.get("volume", ""), "year": it.get("list_year", "")}
        else:
            no = it.get("act_no") or ""
            year = it.get("act_year") or it.get("list_year") or ""
            if not no:
                m = re.search(r"\bAct\s+No\.?\s*(\d+)\s+of\s+(\d{4})", head)
                if m:
                    no, year = m.group(1), m.group(2)
            ytitle = re.search(r"\b(19|20)\d\d\b", title)
            year = year or (ytitle.group(0) if ytitle else "")
            path = os.path.join(repo, "acts", year or "undated", ("act-%s-" % no if no else "") + slug(title)[:80] + ".md")
            meta = {"title": title, "identifier": ("Act No. %s of %s" % (no, year)) if no else "", "type": "act",
                    "year": year}
        if path in seen:
            path = path[:-3] + "-%s.md" % k
        seen.add(path)
        meta.update({"jurisdiction": "zm", "language": "en", "status": "unknown",
                     "source": "https://www.parliament.gov.zm/node/%s" % k, "file": pdfs[0], "retrieved": TODAY})
        if it.get("summary"):
            meta["summary"] = it["summary"][:500]
        write_md(path, meta, title, structure(clean_pages(pages), "en"))
        n += 1
    print("written", n, "skipped", skipped, "not downloaded yet", missing)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
