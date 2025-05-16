from typing import List
import typer
import pandas as pd

from arc.api import FredWrapper, YFWrapper, StatsCanWrapper, EdgarWrapper
from arc.utils import default_logger as logger
import arc.schedule as _sched


app = typer.Typer(
    no_args_is_help=True,
    context_settings=dict(
        help_option_names=["-h", "--help"],
    ),
)


# ────────────────────────────────────────────────────────────
#  global flags
# ────────────────────────────────────────────────────────────
@app.callback(invoke_without_command=False)
def main(
    ctx: typer.Context,
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Bypass local SQLite/TinyDB caches and always hit the remote APIs",
        show_default=True,
    ),
):
    """
    arc - aggregate financial & economic data

    Use --no-cache to force fresh API calls
    """

    ctx.obj = {"cache": not no_cache}


# ────────────────────────────────────────────────────────────
#  sub-commands
# ────────────────────────────────────────────────────────────
# FRED
@app.command()
def fred(
    ctx: typer.Context,
    series_id: str = typer.Argument(..., help="Fred series ID (e.g., CPIAUCSL)"),
    output: str = typer.Option(
        "table", "-o", "--output", help="Output format [excel|csv|chart|table]"
    ),
):
    """Fetch data from Fred"""
    cache = ctx.obj["cache"]
    data = FredWrapper().get_latest_release(series_id, cache=cache)

    _handle_output(data, output, f"{series_id}_fred_data")


# Stats Canada
@app.command()
def statcan(
    ctx: typer.Context,
    vector_id: str = typer.Argument(..., help="StatsCan vector ID (e.g., v41690973)"),
    output: str = typer.Option("table", "-o", "--output"),
):
    """Fetch data from Stats Canada"""
    cache = ctx.obj["cache"]
    data = StatsCanWrapper().get_vector(vector_id, cache=cache)

    _handle_output(data, output, f"{vector_id}_statcan")


# Yahoo Finance
@app.command()
def stock(
    ctx: typer.Context,
    tickers: list[str] = typer.Argument(..., help="ticker symbols to fetch."),
    period: str = typer.Option(
        "1mo", "-p", "--period", help="Data retrieval period (e.g., 1mo, 1y)"
    ),
    interval: str = typer.Option(
        "1d", "-i", "--interval", help="Data interval [1d, 1mo, etc.]"
    ),
    start: str | None = typer.Option(
        None, "-s", "--start", help="Start date for data (YYYY-MM-DD)"
    ),
    end: str | None = typer.Option(
        None, "-e", "--end", help="End date for data (YYYY-MM-DD)"
    ),
    output: str = typer.Option(
        "table", "-o", "--output", help="Output format [excel|csv|chart|table]"
    ),
    columns: list[str] = typer.Option(
        ["Close"],
        "-c",
        "--columns",
        help="Columns to fetch [Close, Open, High, Low, Volume, Dividends, Stock Splits]",
    ),
):
    """Fetch stock data from Yahoo Finance"""
    cache = ctx.obj["cache"]
    columns = [col.title() for col in columns]

    VALID_COLUMNS = {
        "Open",
        "Close",
        "High",
        "Low",
        "Volume",
        "Dividends",
        "Stock Splits",
    }

    invalid_cols = [col for col in columns if col not in VALID_COLUMNS]
    if invalid_cols:
        raise typer.BadParameter(
            f"Invalid columns specified: {invalid_cols}\n"
            f"Valid columns are: {sorted(VALID_COLUMNS)}"
        )

    yf_api = YFWrapper()
    logger.info(f"Fetching data for tickers: {tickers}")

    data = yf_api.get_data(
        tickers,
        period=period,
        interval=interval,
        start=start,
        end=end,
        cache=cache,
    )

    _handle_output(data, output, f"{'_'.join(tickers)}_stock_data")


# ────────────────────────────────────────────────────────────
#  EDGAR
# ────────────────────────────────────────────────────────────
@app.command()
def edgar(
    ctx: typer.Context,
    tickers: list[str] = typer.Argument(
        ..., help="ticker or list of tickers to get json financials from"
    ),
    # cik: str = typer.Argument(..., help="SEC Central Index Key (CIK)"),
    # output: str = typer.Option(
    #     "table", "-o", "--output", help="Output format [excel|csv|chart|table]"
    # ),
):
    """Fetch recent filing metadata from SEC EDGAR"""
    cache = ctx.obj["cache"]
    edgar_api = EdgarWrapper()

    # temporarily have cache=False for now
    edgar_api.get_data(tickers=tickers, cache=False)

    # recent = payload.get("filings", {}).get("recent", {})

    # if not recent:
    #     logger.warning("No recent filings found for CIK %s", cik)
    #     from rich import print as rprint
    #
    #     rprint(payload)
    #     return
    #
    # df = pd.DataFrame(recent)


# ────────────────────────────────────────────────────────────
#  Scheduler sub-commands
# ────────────────────────────────────────────────────────────
scheduler_app = typer.Typer()
app.add_typer(scheduler_app, name="scheduler")


@scheduler_app.command("run")
def schedule_run():
    """start the blocking APScheduler loop (ctrl-c to quit)"""
    _sched.launch()


@scheduler_app.command("once")
def schedule_once():
    """run all refresh jobs once, then exit"""
    _sched.refresh_stocks()
    _sched.refresh_fred()
    logger.info("Manual refresh complete")


# ────────────────────────────────────────────────────────────
#  helpers
# ────────────────────────────────────────────────────────────
def _handle_output(df: pd.DataFrame, kind: str, filename: str):
    match kind:
        case "table":
            from rich import print

            print(df)

        case "csv":
            df.to_csv(f"{filename}.csv")
            logger.info(f"Data exported to {filename}.csv")

        case "excel":
            df.to_excel(f"{filename}.xlsx")
            logger.info(f"Data exported to {filename}.xlsx")

        case "chart":
            import matplotlib.pyplot as plt

            df.plot(title=filename)
            plt.show()

        case _:
            logger.error(
                f"Unsupported output format: {kind}, supported outputs: table, csv, excel, chart"
            )


if __name__ == "__main__":
    app()
