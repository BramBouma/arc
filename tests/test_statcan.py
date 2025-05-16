import types
import builtins
import io

import pandas as pd
import pytest

from arc.api.stats_canada import StatsCanWrapper


class DummyResp:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


def test_statcan_csv(monkeypatch):
    sample = "REF_DATE,VALUE\n2024-01,100\n2024-02,202\n"
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: DummyResp(sample),
    )

    df = StatsCanWrapper().get_vector("v999999", cache=False)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["v999999"]
    assert len(df) == 2
