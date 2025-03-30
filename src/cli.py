import typer
from api import FredWrapper, YFWrapper
from utils import default_logger as logger
import pandas as pd
# from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


app = typer.Typer()


@app.command()
def fred(
    series_id: str = typer.Argument(..., help="Fred series ID (e.g., CPIAUCSL)"),
    output: str = typer.Option("table", "-o", "--output", help="Output format [excel|csv|chart|table]"),
):
    """Fetch data from Fred and display it."""
    fred_api = FredWrapper()
    logger.info(f"Fetching Fred data for series: {series_id}")

    # with Progress(
    #     SpinnerColumn(),
    #     TextColumn("[progress.description]{task.description}"),
    #     TimeElapsedColumn(),
    #     transient=True
    # ) as progress:
    #     task_id = progress.add_task(description="Fetching data from FRED...", total=None)
    #     data = fred_api.get_series_latest_release(series_id)
    #     progress.update(task_id, advance=1)

    data = fred_api.get_latest_release(series_id)

    handle_output(data, output, f"{series_id}_fred_data")


@app.command()
def stock(
    tickers: list[str] = typer.Argument(..., help="List of ticker symbols to fetch."),
    period: str = typer.Option("1mo", "-p", "--period", help="Data retrieval period (e.g., 1mo, 1y)"),
    interval: str = typer.Option("1d", "-i", "--interval", help="Data interval [1d, 1mo, etc.]"),
    start: str = typer.Option(None, "-s", "--start", help="Start date for data (YYYY-MM-DD)"),
    end: str = typer.Option(None, "-e", "--end", help="End date for data (YYYY-MM-DD)"),
    output: str = typer.Option("table", "-o", "--output", help="Output format [excel|csv|chart|table]"),
    columns: list[str] = typer.Option(
        ["Close"],
        "-c",
        "--columns",
        help="Columns to fetch [Close, Open, High, Low, Volume, Dividends, Stock Splits]"
    ),
):
    """Fetch stock data from Yahoo Finance and display it."""

    columns = [col.capitalize() for col in columns]

    VALID_COLUMNS = {
        "Open", "Close", "High", "Low", "Volume", "Dividends", "Stock Splits"
    }

    invalid_cols = [col for col in columns if col not in VALID_COLUMNS]
    if invalid_cols:
        raise typer.BadParameter(
            f"Invalid columns specified: {invalid_cols}\n"
            f"Valid columns are: {sorted(VALID_COLUMNS)}"
        )

    yf_api = YFWrapper()
    logger.info(f"Fetching data for tickers: {tickers}")

    # with Progress(
    #     SpinnerColumn(),
    #     TextColumn("[progress.description]{task.description}"),
    #     TimeElapsedColumn(),
    #     transient=True,
    # ) as progress:
    #     task_id = progress.add_task(description=f"Fetching data for tickers: {tickers}", total=None)
    #     data = yf_api.get_data(
    #         tickers,
    #         period=period,
    #         interval=interval,
    #         start=start,
    #         end=end,
    #     )
    #     progress.update(task_id, advance=1)

    data = yf_api.get_data(
        tickers,
        period=period,
        interval=interval,
        start=start,
        end=end,
    )

    if isinstance(data.columns, pd.MultiIndex):
        data = data.loc[:, (columns, slice(None))]
    else:
        data = data[columns]

    handle_output(data, output, f"{'_'.join(tickers)}_stock_data")


def handle_output(data, output_type, filename):
    if output_type == "table":
        from rich import print
        print(data)

    elif output_type == "csv":
        data.to_csv(f"{filename}.csv")
        logger.info(f"Data exported to {filename}.csv")

    elif output_type == "excel":
        data.to_excel(f"{filename}.xlsx")
        logger.info(f"Data exported to {filename}.xlsx")

    elif output_type == "chart":
        import matplotlib.pyplot as plt
        data.plot(title=filename)
        plt.show()

    else:
        logger.error(f"Unsupported output format: {output_type}")


if __name__ == "__main__":
    app()
