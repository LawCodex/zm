# Zambia (ZM) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Legislation of the Republic of Zambia, in **English**, from the **National Assembly of Zambia**
(https://www.parliament.gov.zm): the chapters of the **Laws of Zambia** (revised edition, Volumes 1–26) and the
**Acts of Parliament** published by year (1997–2026, as enacted), plus the **Constitution** (Cap. 1 as in the
revised edition, and the Constitution of Zambia (Amendment) Act No. 2 of 2016). Retrieved 2026-10-13.

| Category | Files |
|---|---|
| Constitution: Constitution of Zambia Act (Cap. 1, revised edition, Volume 1) and Constitution of Zambia (Amendment) Act, 2016 | 2 |
| Laws of Zambia — chapters (principal Acts, revised edition, Volumes 2–26) | 373 |
| Acts of Parliament, as enacted (1997–2026; mostly 2009–2026) | 553 |
| **Total** | **928** |

## Structure

```
constitution/cap-1-constitution-of-zambia-act.md
constitution/constitution-of-zambia-amendment-act-2016.md
laws-of-zambia/cap-<n>-<slug>.md          Laws of Zambia, Chapter <n> (e.g. cap-2-interpretation-and-general-provisions-act.md)
acts/<year>/act-<no>-<slug>.md            Act No. <no> of <year>
```

Front matter: `identifier` (`Cap. 2`, or `Act No. 72 of 2026`), `volume` (revised-edition volume), `year`,
`status: unknown` (revised-edition chapters are not updated with later amendments; Acts are as enacted),
`source` (the National Assembly page of the Act), `file` (PDF URL), `summary` (long title / description from the
National Assembly page).

Text extracted with poppler `pdftotext`. PART headings and `Section N — <title>` headings were added; section titles
are taken from the "Arrangement of Sections" when present (the marginal note repeating the title is then removed).
The running header "The Laws of Zambia" and the footer "Copyright Ministry of Legal Affairs, Government of the
Republic of Zambia" printed on every page of the revised edition were removed.

## Not covered / known gaps

* 80 PDFs without a usable text layer (scans) were skipped (no OCR) — mainly Acts of 2010–2014 (e.g. Anti-Corruption
  Act 2012, Persons with Disabilities Act 2012, Civil Aviation Authority Act 2012, several Finance/Appropriation and
  amendment Acts) and a few repeal Acts.
* 23 entries of the Acts listing have no document attached on the National Assembly site (e.g. Electronic
  Communications and Transactions Act 2009, Postal Services Act 2009, some 2011–2015 amendment Acts).
* The revised-edition chapters reflect the Laws of Zambia revised edition published on the site (amendments made
  after that edition are only available as separate Acts in `acts/`). Subsidiary legislation (statutory
  instruments) is not included. The ZambiaLII (Zambia Legal Information Institute) site forbids scraping/bulk
  download and was not used.

## Sources and licence

| Source | URL |
|---|---|
| National Assembly of Zambia — Laws of Zambia volumes | https://www.parliament.gov.zm/acts/volumes |
| National Assembly of Zambia — Acts of Parliament | https://www.parliament.gov.zm/acts-of-parliament |

The robots.txt `Crawl-delay: 10` was obeyed (one request every 10 seconds, ≈ 8 hours in total) with an identifying
User-Agent. **Licence / terms:** the revised-edition PDFs carry the footer "Copyright Ministry of Legal Affairs,
Government of the Republic of Zambia", and the National Assembly's "Use Policy" page states that "Permission from
the Clerk of the National Assembly of Zambia is required for any reproduction of, or extended quotation from, the
records, and is usually given provided suitable acknowledgement is made"
(https://www.parliament.gov.zm/node/3595; the page concerns the records held by the National Assembly and its
library). This repository reproduces official legislative texts for non-commercial, informational purposes with
acknowledgement of the source; anyone wishing to reuse them beyond that should seek the Clerk's permission.

## Regenerate

```
pip install -r scripts/requirements.txt     # plus poppler (pdftotext, pdfinfo)
python scripts/zm_fetch.py                  # downloads into ../_raw/zm/ (≈ 8 h because of Crawl-delay: 10)
python scripts/zm_convert.py .
```
