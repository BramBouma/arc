import os
import pytest
from src.api import FredWrapper, YFWrapper


# Ensure API keys are loaded from environment variables
@pytest.fixture(scope="module")
def fred():
    """Returns an instance of FredWrapper using the API key from env vars."""
    api_key = os.getenv("FRED_API_KEY")
    assert api_key, "FRED_API_KEY is not set in environment variables"
    return FredWrapper(api_key=api_key)


@pytest.fixture(scope="module")
def yf():
    """Returns an instance of YFWrapper."""
    return YFWrapper()


def test_fred_get_latest_release(fred):
    """Test fetching data from Fred API using real API key."""
    series_id = "CPIAUCSL"
    data = fred.get_latest_release(series_id)

    assert data is not None
    assert not data.empty
    assert "CPIAUCSL" in data.columns


def test_yf_get_data(yf):
    """Test fetching stock data from Yahoo Finance using real API key."""
    tickers = ["AAPL", "MSFT"]
    data = yf.get_data(tickers, period="1mo")

    assert data is not None
    assert not data.empty
    assert set(tickers).issubset(data.columns.levels[1])
