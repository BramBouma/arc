# arc
- aggregation wrapper around various financial / economic data APIs

## notes
---
### data sources
- currently integrated data sources:
    - Yahoo Finance for public equity data (via YFinance package)
    - FRED for U.S. macro data (via FRED API)
- looking for api integrations for:
    - Stats Canada
    - EDGAR
    - maybe SEDAR but it's notoriously shitty so might be hard
---
### CLI
- currently refactoring cli to rust
- to init python CLI use uv tool install:
    ```bash
    cd arc
    uv tool install .
    ```
- usage:
    - currently organized into two command groups "stock" and "fred"
    - help menu:
    ```bash
    arc --help
    ```
    - subgroup help menus:
    ```bash
    arc stock --help
    arc fred --help
    ```
    - see help menus for arguments and option specifications i can't be bothered to write that rn
---
### local data caching
- data caching in local database with SQLite is still being worked on but should be functional
- data processing is also being refactored to rust so processing logic prolly won't work rn
    - to init run:
    ```bash
    cd arc/database
    sqlite3 arc.db < schema.sql
    ```
    - to verify run:
    ```bash
    sqlite3 arc.db
    ```
    - once inside run to verify schema worked properly:
    ```bash
    .tables
    ```
- will probably port database functionality to a NoSQL database for company fundamentals
    - looking into arcticDB for that
---
### web
- dashboard visualization / other web functionality will probably be with fastapi, flask, or django idk yet
