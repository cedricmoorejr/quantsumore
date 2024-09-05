<p align="center">
  <img src="https://raw.githubusercontent.com/cedricmoorejr/quantsumore/v1.1.0b1/quantsumore/assets/py_quantsumore_logo.png" alt="quantsumore Logo" width="700"/>
</p>

### Summary of the `quantsumore` Library

[![Downloads](https://static.pepy.tech/badge/quantsumore)](https://pepy.tech/project/quantsumore)
[![Downloads](https://static.pepy.tech/badge/quantsumore/month)](https://pepy.tech/project/quantsumore)
[![Downloads](https://static.pepy.tech/badge/quantsumore/week)](https://pepy.tech/project/quantsumore)

The `quantsumore` library is a comprehensive Python package designed for retrieving and analyzing a wide range of financial market data. It provides specialized API clients to fetch data from various financial markets, including cryptocurrencies, equities, Forex, Treasury instruments, and Consumer Price Index (CPI) metrics. The library aims to simplify financial data retrieval and analysis, making it a valuable tool for traders, analysts, researchers, and anyone involved in financial markets. Below is an overview of the key components and functionalities of the `quantsumore` library:

#### 1. **Crypto API Client** (`quantsumore.api.crypto`)
   - **Purpose**: Fetches real-time and historical market data for various cryptocurrencies.
   - **Key Features**:
     - Retrieve the latest live trading data for specified cryptocurrencies.
     - Fetch historical price and trading volume data over a specified date range.
     - Data is returned in structured formats (e.g., pandas DataFrames) for easy analysis.

#### 2. **Equity API Client** (`quantsumore.api.equity`)
   - **Purpose**: Provides detailed information about publicly traded companies.
   - **Key Features**:
     - Fetch company bios, executive details, and other corporate information.
     - Retrieve statistical data, such as market capitalization, P/E ratio, EPS, and more.
     - Get historical stock price data and the latest trading prices.

#### 3. **CPI API Client** (`quantsumore.api.cpi`)
   - **Purpose**: Provides access to Consumer Price Index (CPI) data and tools for inflation adjustments.
   - **Key Features**:
     - Fetch CPI data for all urban consumers.
     - Perform inflation adjustments for specific amounts over different years.
     - Calculate year-by-year and month-by-month inflation-adjusted values.

#### 4. **Forex API Client** (`quantsumore.api.forex`)
   - **Purpose**: Fetches foreign exchange market data, including historical rates and real-time quotes.
   - **Key Features**:
     - Retrieve historical exchange rates for specified currency pairs over defined date ranges.
     - Access interbank rates and perform currency conversions.
     - Get detailed bid and ask prices, quote overviews, and market spreads.

#### 5. **Treasury API Client** (`quantsumore.api.treasury`)
   - **Purpose**: Provides data on U.S. Treasury instruments, including Treasury bills and yield curve rates.
   - **Key Features**:
     - Fetch the latest Treasury bill rates and daily yield curve rates for various maturities.
     - Access comprehensive yield curve data covering short-term bills to long-term bonds.

### Use Cases
- **Investment Research**: The library allows users to analyze market trends, study historical performance, and perform comparative analysis across different asset classes.
- **Economic Analysis**: Access to CPI and Treasury data enables economists to track inflation trends, analyze yield curves, and assess economic conditions.
- **Trading Strategies**: Real-time and historical market data support the development and backtesting of trading strategies for cryptocurrencies, equities, and Forex markets.
- **Risk Management**: Forex and Treasury data can be used to assess currency and interest rate risk, helping businesses and financial institutions manage exposure.




## Table of Contents
- [Using the `crypto` API Client](#using-the-crypto-api-client)
- [Using the `cpi` API Client](#using-the-cpi-api-client)
- [Using the `equity` API Client](#using-the-equity-api-client)
- [Using the `forex` API Client](#using-the-forex-api-client)
- [Using the `treasury` API Client](#using-the-treasury-api-client)



# Using the `crypto` API Client

The `crypto` API client provided by the `quantsumore` package allows users to easily fetch both real-time and historical cryptocurrency market data. This guide will walk you through importing the `crypto` API client and using its methods.

## Importing the Crypto API Client

To start using the `crypto` API client, you need to import it from the `quantsumore.api` package. The `crypto` import provides access to an instance of the `APIClient` class, configured specifically for cryptocurrency data.

```python
from quantsumore.api import crypto
```

## Fetching Latest Cryptocurrency Market Data

To fetch the latest market data for a specific cryptocurrency, you can use the `cLatest` method. This method allows you to specify various parameters, such as the cryptocurrency's slug, base currency, quote currency, exchange, and more.

### Example: Fetching Latest Data for Bitcoin

```python
# Fetch the latest market data for Bitcoin, quoted in USD
latest_data = crypto.cLatest(slug="bitcoin", baseCurrencySymbol="USD", quoteCurrencySymbol="JPY", cryptoExchange="binance", limit=100, exchangeType="all")

# Print the retrieved data
print(latest_data)
```

This example will retrieve the most recent trading data for Bitcoin (BTC) in USD, using the Binance exchange, and display it as a pandas DataFrame.

## Fetching Historical Cryptocurrency Data

To get historical data for a specific cryptocurrency, you can use the `cHistorical` method. You will need to specify the `slug` for the cryptocurrency and the date range (`start` and `end`) for which you want the historical data.

### Example: Fetching Historical Data for Bitcoin

```python
# Fetch historical data for Bitcoin from January 1, 2024, to January 10, 2024
historical_data = crypto.cHistorical(slug="bitcoin", start="2024-01-01", end="2024-01-10")

# Print the historical data
print(historical_data)
```

This example retrieves the historical price and trading volume data for Bitcoin over a specified date range and displays it as a pandas DataFrame.


<br><br>



# Using the `cpi` API Client`

The `cpi` API client provided by the `quantsumore` package allows users to easily fetch Consumer Price Index (CPI) data for all urban consumers and perform inflation adjustments based on historical CPI values. This guide will walk you through importing the `cpi` API client and using its methods.

## Importing the CPI API Client

To start using the `cpi` API client, you need to import it from the `quantsumore.api` package. The `cpi` import provides access to an instance of the `APIClient` class, configured specifically for CPI data.

```python
from quantsumore.api import cpi
```

## Accessing CPI Data and Inflation Adjustment

The `cpi` API client includes a special property called `CPI_U` that provides access to inflation adjustment functionalities.

### 1. Accessing CPI Data for All Urban Consumers

The `CPI_U` property provides CPI data for all urban consumers in the United States. This data is automatically fetched and processed when accessed.

```python
# Access CPI data for all urban consumers
cpi_data = cpi.CPI_U.InflationAdjustment.data

# Display the fetched CPI data
print(cpi_data)
```

### 2. Performing Inflation Adjustments

The `InflationAdjustment` instance allows users to perform various inflation adjustment calculations based on CPI data.

#### Example: Adjusting an Amount Between Years

To calculate the inflation-adjusted value of an amount from one year to another:

```python
# Adjust $100 from the year 2000 to its equivalent in 2024, using July as the reference month
adjusted_value = cpi.CPI_U.InflationAdjustment.select(original_amount=100, original_year=2000, target_year=2024, month_input="July")

# Display the adjusted value
print(f"Adjusted value: ${adjusted_value}")
```

### 3. Year-by-Year Inflation Adjustments

To calculate how the value of a given amount has changed over a specified number of years:

```python
# Calculate how $100 has changed in value over the past 10 years
year_by_year_changes = cpi.CPI_U.InflationAdjustment.year_by_year(original_amount=100, n_years=10)

# Display the year-by-year changes
print(year_by_year_changes)
```

### 4. Month-by-Month Inflation Adjustments for the Current Year

To calculate the inflation-adjusted value of an amount against CPI values for each month of the current year:

```python
# Calculate monthly adjustments for $100 in the current year
month_by_month_adjustments = cpi.CPI_U.InflationAdjustment.month_by_month(amount=100)

# Display the month-by-month adjustments
print(month_by_month_adjustments)
```


<br><br>




# Using the `equity` API Client

The `equity` API client provided by the `quantsumore` package allows users to easily fetch various company-related data, including company bios, executive information, detailed company stats, and both real-time and historical stock price data. This guide will walk you through importing the `equity` API client and using its methods.

## Importing the Equity API Client

To start using the `equity` API client, you need to import it from the `quantsumore.api` package. The `equity` import provides access to an instance of the `APIClient` class, configured specifically for equity (stock) data.

```python
from quantsumore.api import equity
```

## Fetching Company Information

### 1. Company Bio

To fetch an overview or summary of a company's information, use the `CompanyBio` method. This method retrieves the company's description based on its ticker symbol.

```python
# Fetch company bio for Apple Inc. using its ticker symbol 'AAPL'
company_bio = equity.CompanyBio(ticker="AAPL", verbose=True)

# Output will be displayed with a bordered style (if verbose=True)
```

### 2. Company Executives

To get information about a company's executives, use the `CompanyExecutives` method. You can choose to display the information in a tabular format by setting the `verbose` parameter to `True`.

```python
# Fetch information about Apple Inc.'s executives
executive_info = equity.CompanyExecutives(ticker="AAPL", verbose=True)

# Output will be displayed in a tabular format (if verbose=True)
```

### 3. Company Details

To get detailed information about a company, including its website, phone number, address, sector, industry, and more, use the `CompanyDetails` method.

```python
# Fetch detailed company information for Apple Inc.
company_details = equity.CompanyDetails(ticker="AAPL", verbose=True)

# Output will be displayed in a tabular format (if verbose=True)
```

### 4. Company Stats

To retrieve various statistical information and financial metrics about a company, such as prices, volume, market cap, PE ratio, EPS, etc., use the `Stats` method.

```python
# Fetch statistical information for Apple Inc.
company_stats = equity.Stats(ticker="AAPL", verbose=True)

# Output will be displayed in a grid format (if verbose=True)
```

## Fetching Stock Price Data

### 1. Latest Stock Price

To get the latest stock price for a company, use the `sLatest` method. This method provides the most recent price of the stock based on its ticker symbol.

```python
# Fetch the latest stock price for Apple Inc.
latest_price = equity.sLatest(ticker="AAPL")
print(f"Latest stock price for AAPL: {latest_price}")
```

### 2. Historical Stock Price Data

To retrieve historical stock price data for a company over a specified date range, use the `sHistorical` method.

```python
# Fetch historical stock price data for Apple Inc. from January 1, 2024, to January 10, 2024
historical_data = equity.sHistorical(ticker="AAPL", start="2024-01-01", end="2024-01-10")

# Display the historical data
print(historical_data)
```

## Cache Management

The `equity` API client supports caching to improve performance. You can clear the cache for specific tickers or clear all cached data using the `clear_cache` method.

```python
# Clear cached data for a specific ticker
equity.clear_cache(ticker="AAPL")

# Clear all cached data
equity.clear_cache()
```



<br><br>



# Using the `forex` API Client

The `forex` API client provided by the `quantsumore` package allows users to easily fetch various Forex-related data, including historical exchange rates, interbank rates, bid and ask prices, currency conversion rates, and more. This guide will walk you through importing the `forex` API client and using its methods.

## Importing the Forex API Client

To start using the `forex` API client, you need to import it from the `quantsumore.api` package. The `forex` import provides access to an instance of the `APIClient` class, configured specifically for Forex data.

```python
from quantsumore.api import forex
```

## Fetching Forex Data

### 1. Historical Exchange Rates

To fetch historical exchange rates for a specific currency pair over a defined date range, use the `fHistorical` method.

```python
# Fetch historical exchange rates for EUR/USD from January 1, 2024, to January 10, 2024
historical_data = forex.fHistorical(currency_pair="EURUSD", start="2024-01-01", end="2024-01-10")

# Display the historical data
print(historical_data)
```

### 2. Interbank Exchange Rates

To get interbank exchange rates for a specified currency and optionally filter the data based on included or excluded countries or regions, use the `Interbank` method.

```python
# Fetch interbank rates for USD, including only specific countries
interbank_data = forex.Interbank(currency_code="USD", include=["US", "EU"], verbose=True)

# The data will be displayed in a tabular format if verbose=True
```

### 3. Quote Overview

To get a detailed overview of Forex trading data for a specific currency pair, use the `QuoteOverview` method.

```python
# Fetch a quote overview for EUR/USD
quote_data = forex.QuoteOverview(currency_pair="EURUSD", verbose=True)

# The data will be displayed in a detailed format if verbose=True
```

### 4. Bid and Ask Prices

To retrieve the current bid and ask prices, along with the spread for a specific currency pair, use the `BidAsk` method.

```python
# Fetch bid and ask prices for EUR/USD
bid_ask_data = forex.BidAsk(currency_pair="EURUSD", verbose=True)

# The data will be displayed in a grid format if verbose=True
```

### 5. Currency Conversion

To convert an amount from one currency to another based on the latest conversion rates, use the `CurrencyConversion` method.

```python
# Convert 100 Euros to USD based on the latest conversion rates
conversion_data = forex.CurrencyConversion(currency_pair="EURUSD", conversion_amount=100, verbose=True)

# The conversion details will be displayed in a table format if verbose=True
```

## Cache Management

The `forex` API client supports caching to improve performance. You can clear the cache for specific currencies or clear all cached data using the `clear_cache` method.

```python
# Clear cached data for a specific currency (e.g., EUR)
forex.clear_cache(currency="EUR")

# Clear all cached data
forex.clear_cache()
```


<br><br>


# Using the `treasury` API Client

The `treasury` API client provided by the `quantsumore` package allows users to easily fetch U.S. Treasury-related data, including Treasury bill rates, yield curve rates for various maturities, and comprehensive yield curve rates. This guide will walk you through importing the `treasury` API client and using its methods.

## Importing the Treasury API Client

To start using the `treasury` API client, you need to import it from the `quantsumore.api` package. The `treasury` import provides access to an instance of the `APIClient` class, configured specifically for U.S. Treasury data.

```python
from quantsumore.api import treasury
```

## Fetching Treasury Data

### 1. Fetching Treasury Bill Rates

To fetch the most up-to-date daily Treasury bill rates, use the `TBill` method. You can specify a time period to narrow down the data.

```python
# Fetch the latest Treasury bill rates for the current year
tbill_rates = treasury.TBill(period="CY")

# Display the fetched Treasury bill rates
print(tbill_rates)
```

- **Parameters**:
  - `period`: Optional. Use 'CY' for the current year, a specific year (e.g., 2021), or a year and month (e.g., 202308). If no period is specified, the current month of the current year is used.

### 2. Fetching Daily Treasury Yield Curve Rates

To get the latest yield curve rates for U.S. Treasury notes and bonds with specific maturities, use the `Yield` method.

```python
# Fetch the latest yield curve rates for the year 2023
yield_rates = treasury.Yield(period=2023)

# Display the fetched yield curve rates
print(yield_rates)
```

- **Parameters**:
  - `period`: Optional. Use 'CY' for the current year, a specific year (e.g., 2021), or a year and month (e.g., 202308). If no period is specified, the current month of the current year is used.

### 3. Fetching Comprehensive Treasury Yield Curve Rates

To fetch a more comprehensive set of Treasury yield curve rates covering various maturities, use the `YieldAll` method.

```python
# Fetch comprehensive Treasury yield curve rates for August 2024
yield_all_rates = treasury.YieldAll(period=202408)

# Display the fetched comprehensive yield curve rates
print(yield_all_rates)
```

- **Parameters**:
  - `period`: Optional. Use 'CY' for the current year, a specific year (e.g., 2021), or a year and month (e.g., 202308). If no period is specified, the current month of the current year is used.
