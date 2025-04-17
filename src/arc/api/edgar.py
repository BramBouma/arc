import requests
from arc.utils import default_logger as logger
from document_store import doc_db

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {"User-Agent": "arc/0.1 (your.email@example.com)"}


class EdgarWrapper:
    """
    Minimal EDGAR wrapper that grabs the submissions JSON
    and caches the raw blob in TinyDB.
    """

    def fetch_submissions(self, cik: str, cache: bool = True) -> dict:
        cik_padded = cik.zfill(10)
        table = "edgar_submissions"

        if cache:
            cached = doc_db.get(table, cik=cik_padded)
            if cached:
                logger.info(f"EDGAR: loaded CIK {cik} from TinyDB cache")
                return cached["payload"]

        logger.info(f"EDGAR: fetching CIK {cik} from SEC")
        resp = requests.get(
            SEC_SUBMISSIONS.format(cik=cik_padded), headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
        payload = resp.json()

        # upsert by CIK
        doc_db.upsert(
            table,
            {"cik": cik_padded, "payload": payload},
            keys=["cik"],
        )
        return payload
