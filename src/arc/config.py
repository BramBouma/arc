import os
from arc.utils import default_logger as logger, ConfigurationError

# API endpoints
FRED_API_URL = "https://api.stlouisfed.org/fred/"
STATS_CANADA_API_URL = "https://api.statcan.gc.ca/"
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/"
EDGAR_API_URL = "https://data.sec.gov/"


# ────────────────────────────────────────────────────────────
#  env‑var helper
# ────────────────────────────────────────────────────────────
def get_env_var(var_name: str, default=None) -> str:
    """Return an environment variable or raise if missing and no default."""
    value = os.getenv(var_name, default)
    if value is None:
        logger.error(f"'{var_name}' is not set")
        raise ConfigurationError(f"'{var_name}' is not set")
    logger.info(f"Loaded environment variable for {var_name}")
    return value


# ────────────────────────────────────────────────────────────
#  API‑key getters
# ────────────────────────────────────────────────────────────
def get_fred_api_key() -> str:
    return get_env_var("FRED_API_KEY")


def get_sc_api_key() -> str:
    return get_env_var("STATS_CANADA_API_KEY")


def get_edgar_api_key() -> str:
    return get_env_var("EDGAR_API_KEY")


# ────────────────────────────────────────────────────────────
#  EDGAR helpers
# ────────────────────────────────────────────────────────────
def get_edgar_headers() -> dict[str, str]:
    """
    Return SEC‑compliant headers for EDGAR calls.

    The SEC requires that all requests contain a descriptive **User‑Agent**
    with contact information.  Set ``EDGAR_USER_AGENT`` in your environment
    to override the default.
    """
    ua = os.getenv("EDGAR_USER_AGENT", "arc/0.1 (your.email@example.com)")
    # return {"User-Agent": ua}
    return ua
