import os
from utils import default_logger as logger, ConfigurationError

# API endpoints
FRED_API_URL = "https://api.stlouisfed.org/fred/"
STATS_CANADA_API_URL = "https://api.statcan.gc.ca/"
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/"
EDGAR_API_URL = "https://data.sec.gov/"


def get_env_var(var_name: str, default=None) -> str:
    """
    gets environment variable
    """
    value = os.getenv(var_name, default)
    if value is None:
        logger.error(f"'{var_name}' is not set")
        raise ConfigurationError(f"'{var_name}' is not set")
    logger.info(f"Loaded environment variable for {var_name}")
    return value


# lazy-loaded getters for API keys
def get_fred_api_key() -> str:
    return get_env_var("FRED_API_KEY")


def get_sc_api_key() -> str:
    return get_env_var("STATS_CANADA_API_KEY")


def get_edgar_api_key() -> str:
    return get_env_var("EDGAR_API_KEY")

# Other global settings
# DEBUG = os.getenv("DEBUG", "True") == "True"
# DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///data_report.db")
