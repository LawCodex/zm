# Zambia (ZM) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Work in progress: the corpus is being downloaded from the National Assembly of Zambia
(https://www.parliament.gov.zm), whose robots.txt asks for a 10-second crawl delay. Counts will be added when the
download is complete.

## Regenerate

```
pip install -r scripts/requirements.txt     # plus poppler (pdftotext, pdfinfo)
python scripts/zm_fetch.py                  # downloads into ../_raw/zm/
python scripts/zm_convert.py .
```
