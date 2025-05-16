import requests
from arc.utils import default_logger as logger
from arc.config import EDGAR_API_URL, get_edgar_headers
from arc.database.document_store import doc_db

SEC_SUBMISSIONS = f"{EDGAR_API_URL.rstrip('/')}/submissions/CIK{{cik}}.json"
SEC_COMPANYFACTS = f"{EDGAR_API_URL.rstrip('/')}/api/xbrl/companyfacts/CIK{{cik}}.json"
HEADERS = get_edgar_headers()


class EdgarWrapper:
    """
    Minimal EDGAR wrapper that grabs the submissions JSON
    and caches the raw blob in TinyDB.
    """

    def fetch_submissions(self, cik: str, cache: bool = True) -> dict:
        cik_padded = cik.zfill(10)
        table = "edgar_submissions"

        # ───── SQLite‑like TinyDB cache ────────────────────────────────
        if cache:
            cached = doc_db.get(table, cik=cik_padded)
            if cached:
                logger.info("EDGAR: loaded CIK %s from TinyDB cache", cik_padded)
                return cached["payload"]

        # ───── Remote fetch ────────────────────────────────────────────
        logger.info("EDGAR: fetching CIK %s from SEC", cik_padded)
        resp = requests.get(
            SEC_SUBMISSIONS.format(cik=cik_padded),
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()

        # upsert by CIK so we keep only the latest blob per company
        doc_db.upsert(
            table,
            {"cik": cik_padded, "payload": payload},
            keys=["cik"],
        )
        return payload

    def fetch_companyfacts(self, cik: str, cache: bool = True) -> dict:
        cik_padded = cik.zfill(10)
        table = "edgar_submissions"

        # ───── SQLite‑like TinyDB cache ────────────────────────────────
        if cache:
            cached = doc_db.get(table, cik=cik_padded)
            if cached:
                logger.info("EDGAR: loaded CIK %s from TinyDB cache", cik_padded)
                return cached["payload"]

        # ───── Remote fetch ────────────────────────────────────────────
        logger.info("EDGAR: fetching CIK %s from SEC", cik_padded)
        resp = requests.get(
            SEC_COMPANYFACTS.format(cik=cik_padded),
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()

        # upsert by CIK so we keep only the latest blob per company
        doc_db.upsert(
            table,
            {"cik": cik_padded, "payload": payload},
            keys=["cik"],
        )
        return payload
