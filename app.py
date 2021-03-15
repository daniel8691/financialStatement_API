# from config import model_api
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# import streamlit
import streamlit as st
# import datareader for company historical data
from pandas_datareader import data as wb

# test api key
model_api = "b988be4ae1ef1a05b6f97847053ea6e5"

# disable all warnings
st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(layout="wide")

# create streamlit sidebar to display input boxes
col1 = st.sidebar
# set column layouts. col2 have twice to width as col3
col2, col3 = st.beta_columns((2,1))

col1.header("Input Options")
# store inputs to build urls
ticker = st.sidebar.text_input("Input your company ticker").upper()
period = st.sidebar.selectbox("Select the Reporting Period", ("Annual", "Quarter")).lower()
moving_avg_input = int(st.sidebar.number_input("Insert a Second Moving Average"))

col2.title(f"Company Analysis for {ticker}")

# code check
# st.write("current iteration is", ticker, "and", period)

if ticker != 0:
    incomeAnnual_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={model_api}"
    # get income statement data
    incomeQuarter_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={model_api}&period={period}&limit=100"

    # get cash flow statement data
    cashFlowQuarter_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={model_api}&period={period}&limit=100"

    # get balance sheet data
    balanceSheet_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}&limit=400&apikey={model_api}"

    # income statement growth numbers
    incomeGrowthQuarter_url = f"https://financialmodelingprep.com/api/v3/income-statement-growth/{ticker}?limit=100&period={period}&apikey={model_api}"

    # key stats investors look for
    keyStats_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={model_api}"

    # key metrics
    keyMetrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period={period}&limit=100&apikey={model_api}"

    # enterprise value
    enterpriseValue_url = f"https://financialmodelingprep.com/api/v3/enterprise-values/{ticker}?period={period}&limit=100&apikey={model_api}"

    # insider trading info
    insider_url = f"https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker}&limit=100&apikey={model_api}"

    # Request for data in json formats
    income_json = requests.get(incomeQuarter_url).json()
    cashFlow_json = requests.get(cashFlowQuarter_url).json()
    keyMetrics_json = requests.get(keyMetrics_url).json()
    balance_json = requests.get(balanceSheet_url).json()
    enterpriseValue_json = requests.get(enterpriseValue_url).json()

###############################################
# INCOME STATEMENT ANALYSIS
###############################################

# create a funciton that outputs all financial statement information
def createIncomeStatement(incomeStatement_file):
    """
    THIS FUNCTION CREATES A DATAFRAME FROM INCOME STATEMENT DATA
    """
    for i in range(len(incomeStatement_file)):
        # define the rows for the DataFrame
        rows = ["Revenue",
                "Revenue Growth",
                "Cost of Revenue",
                "Gross Profit",
                'Operating Margin', 
                "Operating Income/Loss", 
                "Operating Income/Loss Growth",                  
                "Net Income",
               "Net Margin"]

        # determine revenue
        revenue = incomeStatement_file[i]['revenue'] / 1000
        # determine revenue growth
        try:
            revenuePreviousQuarter = incomeStatement_file[i+1]['revenue'] / 1000
            revenueGrowth = (revenue - revenuePreviousQuarter) / revenuePreviousQuarter
        except IndexError:
            revenueGrowth = np.nan
        except ZeroDivisionError:
            revenueGrowth = np.nan
        # determine cost of revenue
        costRevenue = incomeStatement_file[i]['costOfRevenue'] / 1000
        # determine gross profit
        gross_profit = incomeStatement_file[i]['grossProfit'] / 1000
        # determine operating expenses
        operating_expenses = incomeStatement_file[i]['operatingExpenses'] / 1000
        # determine net income
        net_income = incomeStatement_file[i]['netIncome'] / 1000
        # calculate operating income
        operating_income = gross_profit - operating_expenses
        # operating income growth
        try:
            grossProfitPreviousQuarter = incomeStatement_file[i+1]['grossProfit'] / 1000
            operatingExpensesPreviousQuarter = incomeStatement_file[i+1]['operatingExpenses'] / 1000
            operatingIncomePreviousQuarter = grossProfitPreviousQuarter - operatingExpensesPreviousQuarter
            operating_income_growth = (operating_income - operatingIncomePreviousQuarter) / operatingIncomePreviousQuarter
        except IndexError:
            operating_income_growth = np.nan
        except ZeroDivisionError:
            operating_income_growth = np.nan
        
        # calculate operating margin if revenue is greater than 0
        try:
            operating_margin = operating_income / revenue
        except ZeroDivisionError:
            operating_margin = np.nan
            
        # Calculate net margin
        try:
            netMargin = net_income / revenue
        except ZeroDivisionError:
            netMargin = np.nan
        
        
        # create a dataframe on the first iteration and add new columns on the rest 
        if i == 0:
            df = pd.DataFrame({incomeStatement_file[i]['date']: [revenue,
                                                                 revenueGrowth,
                                                                 costRevenue,
                                                                 gross_profit,
                                                                 operating_margin, 
                                                                 operating_income,
                                                                 operating_income_growth,                                                               
                                                                 net_income,
                                                                 netMargin]}, 
                                                         index=rows)
        else:
            df[incomeStatement_file[i]['date']] = [revenue,
                                                   revenueGrowth,
                                                   costRevenue,
                                                   gross_profit,
                                                   operating_margin, 
                                                   operating_income,
                                                   operating_income_growth,                                                   
                                                   net_income,
                                                   netMargin]
    # display company ticker as index title
    df.index.name = f"{incomeStatement_file[0]['symbol']} (in thousands)"

    return df

###############################################
# CASH FLOW ANALYSIS
###############################################

# build a cash flow statement
# Create a function that creates the cash flow statement
def createCashFlowStatement(cashFlow_file):
    """
    This function creates a dataframe with key information from the cash flow statement
    """
    # find whether the company pays a dividend
    dividend_list = [cashFlow_file[div]['dividendsPaid'] for div in range(len(cashFlow_file))]        
        
    for num in range(len(cashFlow_file)):        
        # define the index for the dataframe
        # add a dividend row if the company pays a dividend
        if sum(dividend_list) != 0:
            cashRows = ["cash from operating activities",
                   "cash used for investing activities",
                   "cash used provided by financing activities",
                   "acquisitions",
                   "purchase of investments",
                   "sales maturities of investments",
                   "net change in cash",
                   "FREE CASH FLOW",
                    "dividends paid",
                    "debt repayments",
                   "common stock repurchased"]        
        else: 
            cashRows = ["cash from operating activities",
                       "cash used for investing activities",
                       "cash used provided by financing activities",
                       "acquisitions",
                       "purchase of investments",
                       "sales maturities of investments",
                       "net change in cash",
                       "FREE CASH FLOW",
                        "debt repayments",
                       "common stock repurchased"]
        cashOperatingActivities = cashFlow_file[num]['netCashProvidedByOperatingActivities'] / 1000 
        cashInvestingActivities = cashFlow_file[num]['netCashUsedForInvestingActivites'] / 1000
        cashFinancingActivities = cashFlow_file[num]['netCashUsedProvidedByFinancingActivities'] / 1000
        acquisitions = cashFlow_file[num]['acquisitionsNet'] / 1000
        purchaseInvestments = cashFlow_file[num]['purchasesOfInvestments'] / 1000
        investmentMaturities = cashFlow_file[num]['salesMaturitiesOfInvestments'] / 1000
        changeCash = cashFlow_file[num]['netChangeInCash'] / 1000
        freeCashFlow = cashFlow_file[num]['freeCashFlow'] / 1000
        stockRepurchase = cashFlow_file[num]['commonStockRepurchased'] / 1000
        # Debt repayments
        debtRepayments = cashFlow_file[num]['debtRepayment'] / 1000
        # dividend data
        dividend = cashFlow_file[num]['dividendsPaid'] / 1000

        # do this if the company doesn't pay a dividend
        if sum(dividend_list) == 0:
            # create a dataframe on the first iteration and add new columns on the rest 
            if num == 0: 
                df = pd.DataFrame({cashFlow_file[num]['date']: [cashOperatingActivities,
                                                    cashInvestingActivities,
                                                    cashFinancingActivities,
                                                    acquisitions,
                                                    purchaseInvestments,
                                                    investmentMaturities,
                                                    changeCash,
                                                    freeCashFlow,
                                                    debtRepayments,
                                                    stockRepurchase]}, 
                                                 index=cashRows)

            else:
                df[cashFlow_file[num]['date']] = [cashOperatingActivities,
                                                    cashInvestingActivities,
                                                    cashFinancingActivities,
                                                    acquisitions,
                                                    purchaseInvestments,
                                                    investmentMaturities,
                                                    changeCash,
                                                    freeCashFlow,
                                                    debtRepayments,
                                                    stockRepurchase]
        # this dataframe will include a DIVIDENDS row
        else:
            if num == 0: 
                df = pd.DataFrame({cashFlow_file[num]['date']: [cashOperatingActivities,
                                                    cashInvestingActivities,
                                                    cashFinancingActivities,
                                                    acquisitions,
                                                    purchaseInvestments,
                                                    investmentMaturities,
                                                    changeCash,
                                                    freeCashFlow,
                                                    dividend,
                                                    debtRepayments,
                                                    stockRepurchase]}, 
                                                 index=cashRows)

            else:
                df[cashFlow_file[num]['date']] = [cashOperatingActivities,
                                                    cashInvestingActivities,
                                                    cashFinancingActivities,
                                                    acquisitions,
                                                    purchaseInvestments,
                                                    investmentMaturities,
                                                    changeCash,
                                                    freeCashFlow,
                                                    dividend,
                                                    debtRepayments,
                                                    stockRepurchase]
            
    # display company ticker as index title
    df.index.name = f"{cashFlow_file[0]['symbol']} (in thousands)"
    
    return df

###############################################
# BALANCE SHEET ANALYSIS
###############################################

# create a balance sheet
def createBalanceSheet(balanceSheetFile):
    """
    This function creates a balance sheet
    """
    for num in range(len(balanceSheetFile)):
        balanceRows = ["current assets",
                   "current liabilities",
                   "retained earnings",                   
                   "shareholder equity"]
        
        # find current assets
        currentAsset = balanceSheetFile[num]['totalCurrentAssets'] / 1000
        #find current liabilities
        currentLiabilities = balanceSheetFile[num]['totalCurrentLiabilities'] / 1000
        # find retained earnings
        retainedEarning = balanceSheetFile[num]['retainedEarnings'] / 1000
        #find shareholders equity
        shareholderEquity = balanceSheetFile[num]['totalStockholdersEquity'] / 1000



        
        # create a dataframe on the first iteration and add new columns on the rest 
        if num == 0: 
            df = pd.DataFrame({balanceSheetFile[num]['date']: [currentAsset,
                                                           currentLiabilities,
                                                           retainedEarning,
                                                           shareholderEquity]}, 
                                             index=balanceRows)
        else:
            df[balanceSheetFile[num]['date']] = [currentAsset,
                                           currentLiabilities,
                                           retainedEarning,
                                           shareholderEquity]
            
    # display company ticker as index title
    df.index.name = f"{balanceSheetFile[0]['symbol']} (in thousands)"
    
    return df

###############################################
# KEY RATIOS ANALYSIS
###############################################

# create key ratios dataframe
def createKeyRatios(balanceSheet, incomeStatement, cashFlow, enterpriseValue):
    # loop through all the elements in the json list
    for num in range(len(balanceSheet)):
        
        # define the rows/index for the dataframe
        keyRows = ["EPS",
                   "PS ratio",
                   "PE ratio",
                   "Asset coverage",
                  "Goodwill to Asset ratio",
                  "Current ratio",
                   "Return on Assets",
                  'Return on Equity',
                  'Price to book ratio',
                   'Enterprise value to sales',
                  'Net margin']
        
            
        # calculate Asset coverage ratio
        totalAssets = balanceSheet[num]['totalAssets'] / 1000
        intangibleAssets = balanceSheet[num]["intangibleAssets"] / 1000
        currentLiabilities = balanceSheet[num]['totalCurrentLiabilities'] / 1000
        shortTermDebt = balanceSheet[num]["shortTermDebt"] / 1000
        totalDebt = balanceSheet[num]['totalDebt'] / 1000
        # get rid of division by zero error total debt is 0
        try:
            assetCoverage = ((totalAssets - intangibleAssets) -
                            (currentLiabilities - shortTermDebt)) / totalDebt
        except ZeroDivisionError:
            assetCoverage = np.nan

        # calculate goodwill to asset ratio
        goodwill = balanceSheet[num]['goodwill'] / 1000
        goodwillAsset = goodwill / totalAssets
        
        # calculate current ratio
        currentAssets = balanceSheet[num]['totalCurrentAssets'] / 1000
        currentRatio =  currentAssets / currentLiabilities
        
        # calculate the return on asset
        net_income = incomeStatement[num]['netIncome'] / 1000
        ROA = net_income / totalAssets
        
        # find return on equity
        shareholderEquity = balanceSheet[num]['totalStockholdersEquity'] / 1000
        try:
            ROE = net_income / shareholderEquity 
        except ZeroDivisionError:
            ROE = np.nan
        
        # find price to book ratio (market cap / (total asset - total liability))
        marketCap = enterpriseValue[num]['marketCapitalization'] / 1000
        try:            
            PB = marketCap / (shareholderEquity * 1000)
        except IndexError:
            PB = np.nan
        except ZeroDivisionError:
            PB = np.nan
        
        # find earnings per share
        EPS = incomeStatement[num]["eps"]
        
        # calculate price to sales ratio
        revenue = incomeStatement[num]['revenue'] / 1000
        try:
            PS_ratio = marketCap / revenue
        except ZeroDivisionError:
            PS_ratio = np.nan          
        
        # calculate price to earnings ratio
        marketValuePerShare = enterpriseValue[num]['stockPrice']
        # prevent divisionbyzero error
        try:
            PE_ratio = marketValuePerShare / EPS
        except ZeroDivisionError:
            PE_ratio = np.nan    
            
        # calculate the net marin
        try:
            netMargin = net_income / revenue
        except ZeroDivisionError:
            netMargin = np.nan
        
        # calculate enterprise value to sales ratio
        EV = enterpriseValue[num]['enterpriseValue'] / 1000
        try:
            EV_sales =  EV / revenue
        except:
            EV_sales = np.nan
        
        # create a dataframe on the first iteration and add new columns on the rest 
        if num == 0: 
            df = pd.DataFrame({balanceSheet[num]['date']: [EPS,
                                                           PS_ratio,
                                                           PE_ratio,
                                                           assetCoverage,
                                                           goodwillAsset,
                                                           currentRatio,
                                                           ROA,
                                                           ROE,
                                                           PB,
                                                           EV_sales,
                                                          netMargin]}, 
                                             index=keyRows)
        else:
            df[balanceSheet[num]['date']] = [EPS,
                                             PS_ratio,
                                             PE_ratio,
                                             assetCoverage,
                                             goodwillAsset,
                                             currentRatio,
                                             ROA,
                                             ROE,
                                             PB,
                                             EV_sales,
                                            netMargin]
            
    # display company ticker as index title
    df.index.name = balanceSheet[0]['symbol']
    
    return df

###############################################
# INSIDER ANALYSIS
###############################################

def insider_analysis(input_ticker):
    """
    This function outputs:
    Dataframe, total insider purchases, total insider sales, average insider purchase price and average insider sale price
    """
    # insider information webscrapping (first 100 results)
    insider_url_pageLoop = f"http://openinsider.com/screener?s={input_ticker.lower()}&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1"
    # read html table and take the 3rd table from the last element in the list
    insider_df = pd.read_html(insider_url_pageLoop)[-3]
    # drop unneccessary columns
    try:
        insider_df.drop(columns=["X",'1d', '1w',
           '1m', '6m' ], inplace=True)

        # change column names
        insider_df.columns = insider_df.rename(str.lower, axis= "columns").columns.\
            str.replace("δown","change_in_ownership").\
            str.replace("\s","_")

        # remove all special characters in the "value" column
        insider_df['value'] = insider_df['value'].replace({"\$":"",
                                    "\,":"",
                                    "\-":"",
                                    "\+":""}, regex=True)

        # remove all special characters in the "price" column
        insider_df['price'] = insider_df['price'].replace({"\$":"",
                                    "\,":""}, regex=True)

        # change data type to float for the "value" and "price" columns
        insider_df['value'] = insider_df['value'].astype(float)
        insider_df['price'] = insider_df['price'].astype(float)

        # find the sum of insider purchases and sales
        total_insider_purchases = insider_df[insider_df['trade_type'].str.contains("Purchase")]['value'].sum()
        total_insider_sales = insider_df[insider_df['trade_type'].str.contains("Sale")]['value'].sum()

        # change filing and trade dates to pandas datetime objects
        # first get rid of the hours/min/seconds data (not sure what I can do with this info)
        insider_df['filing_date'] = [insider_df['filing_date'][num].split(" ")[0] for num in range(len(insider_df))]
        # convert in Year-month-day format
        insider_df['filing_date'] = pd.to_datetime(insider_df['filing_date'])
        insider_df['trade_date'] = pd.to_datetime(insider_df['trade_date'])

        # find the mean purchase and sale price
        average_insider_purchasePrice = round((insider_df[insider_df['trade_type'].str.contains("Purchase")]['price'].mean()), 2)
        average_insider_salePrice = round((insider_df[insider_df['trade_type'].str.contains("Sale")]['price'].mean()), 2)
    
    except KeyError:
        print("No insider information found")

    # return all calculated values
    return insider_df, total_insider_purchases, total_insider_sales, average_insider_purchasePrice, average_insider_salePrice


###############################################
# HISTORICAL DATA ANALYSIS
###############################################

def moving_avg_analysis(company_ticker, moving_avg_days):
    # get the historical data
    historical_data = wb.DataReader(company_ticker, data_source="yahoo")

    # select only the last 1000 days of daily prices
    historical_data = historical_data.iloc[-1000:][["Volume", 'Adj Close']]

    # select only the last 1200 days of prices
    historical_data['20d'] = historical_data['Adj Close'].rolling(20).mean()
    historical_data[f'{moving_avg_days}d'] = historical_data['Adj Close'].rolling(moving_avg_days).mean()

    # graph
    historical_data[['Adj Close', '20d', f'{moving_avg_days}d']].plot(figsize=(15,12))
    plt.style.use(["seaborn-whitegrid"])

    # set x,y labels, tick size and legend size
    plt.xlabel("Date", fontsize=18)
    plt.ylabel("Price", fontsize=18)
    plt.xticks(fontsize= 14)
    plt.yticks(fontsize=14)
    plt.legend(title = "Legend",
               loc="best",
               labels = ["Adj Close",
                        "20-day Moving Average",
                        f"{moving_avg_days}-day Moving Average"],
               fontsize=15,
               title_fontsize=20,
               frameon = True)

###############################################
# RSI ANALYSIS
###############################################



income_df = createIncomeStatement(income_json)
cashFlow_df = createCashFlowStatement(cashFlow_json)
balanceSheet_df = createBalanceSheet(balance_json)
keyMetrics_df = createKeyRatios(balance_json, income_json, cashFlow_json, enterpriseValue_json)
# insider analysis results
insider_df, insider_purchases, insider_sales, avg_insiderPurchased, avg_insiderSold = insider_analysis(ticker)

# DISPLAY ALL WEBPAGE INFO
col2.dataframe(income_df)
col2.dataframe(cashFlow_df)
col2.dataframe(balanceSheet_df)
col2.dataframe(keyMetrics_df)
# insider info
col2.dataframe(insider_df)
col3.text(f"Total Insider Purchases (Value): {insider_purchases}")
col3.text(f"Total Insider Sold (Value): {insider_sales}")
col3.text(f"Average Price of Insider Purchases: {avg_insiderPurchased}")
col3.text(f"Average Price of Insider Sales: {avg_insiderSold}")
# momentum analysis
col2.header("Moving Average Analysis")
if (ticker != 0) and (moving_avg_input != 0):
    moving_avg_fig = moving_avg_analysis(ticker, int(moving_avg_input))
    col2.pyplot(moving_avg_fig)

