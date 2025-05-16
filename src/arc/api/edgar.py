from typing import List
import json
import requests
from arc.utils import default_logger as logger
from arc.config import EDGAR_API_URL, get_edgar_headers
from arc.database.document_store import doc_db

from secedgar.core.rest import get_company_facts


class EdgarWrapper:
    """
    Wrapper around get_company_facts method from secedgar library
    (https://github.com/sec-edgar/sec-edgar)
    Local json blob caching in TinyDB and returns raw json
    """

    def __init__(self) -> None:
        self.user_agent: str = get_edgar_headers()
        # logger.info("EDGARWrapper initialized")

    def get_data(
        self,
        tickers: List[str] | str,
        cache: bool = False,
    ) -> None:
        tickers_iter = (
            [t.upper() for t in tickers]
            if isinstance(tickers, list)
            else [tickers.upper()]
        )

        data_dict: dict = get_company_facts(
            lookups=tickers_iter, user_agent=self.user_agent
        )

        data_json = json.dumps(data_dict, indent=4)

        print(data_json)

        # SEC_SUBMISSIONS = f"{EDGAR_API_URL.rstrip('/')}/submissions/CIK{{cik}}.json"
        # SEC_COMPANYFACTS = f"{EDGAR_API_URL.rstrip('/')}/api/xbrl/companyfacts/CIK{{cik}}.json"
        # HEADERS = get_edgar_headers()

        # class EdgarWrapper:
        #     """
        #     Minimal EDGAR wrapper that grabs the submissions JSON
        #     and caches the raw blob in TinyDB.
        #     """
        #
        #     def fetch_submissions(self, cik: str, cache: bool = True) -> dict:
        #         cik_padded = cik.zfill(10)
        #         table = "edgar_submissions"
        #
        #         # ───── SQLite‑like TinyDB cache ────────────────────────────────
        #         if cache:
        #             cached = doc_db.get(table, cik=cik_padded)
        #             if cached:
        #                 logger.info("EDGAR: loaded CIK %s from TinyDB cache", cik_padded)
        #                 return cached["payload"]
        #
        #         # ───── Remote fetch ────────────────────────────────────────────
        #         logger.info("EDGAR: fetching CIK %s from SEC", cik_padded)
        #         resp = requests.get(
        #             SEC_SUBMISSIONS.format(cik=cik_padded),
        #             headers=HEADERS,
        #             timeout=15,
        #         )
        #         resp.raise_for_status()
        #         payload = resp.json()
        #
        #         # upsert by CIK so we keep only the latest blob per company
        #         doc_db.upsert(
        #             table,
        #             {"cik": cik_padded, "payload": payload},
        #             keys=["cik"],
        #         )
        #         return payload
        #
        #     def fetch_companyfacts(self, cik: str, cache: bool = True) -> dict:
        #         cik_padded = cik.zfill(10)
        #         table = "edgar_submissions"
        #
        #         # ───── SQLite‑like TinyDB cache ────────────────────────────────
        #         if cache:
        #             cached = doc_db.get(table, cik=cik_padded)
        #             if cached:
        #                 logger.info("EDGAR: loaded CIK %s from TinyDB cache", cik_padded)
        #                 return cached["payload"]
        #
        #         # ───── Remote fetch ────────────────────────────────────────────
        #         logger.info("EDGAR: fetching CIK %s from SEC", cik_padded)
        #         resp = requests.get(
        #             SEC_COMPANYFACTS.format(cik=cik_padded),
        #             headers=HEADERS,
        #             timeout=15,
        #         )
        #         resp.raise_for_status()
        #         payload = resp.json()
        #
        #         # upsert by CIK so we keep only the latest blob per company
        #         doc_db.upsert(
        #             table,
        #             {"cik": cik_padded, "payload": payload},
        #             keys=["cik"],
        #         )
        #         return payload
