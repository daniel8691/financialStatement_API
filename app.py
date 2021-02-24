from config import model_api
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

# import streamlit
import streamlit as st




st.set_page_config(layout="wide")

col1 = st.sidebar
col2, col3 = st.beta_columns((2,1))

col1.header("Input Options")
# store inputs to build urls
ticker = st.sidebar.text_input("Input your company").upper()
period = st.sidebar.selectbox("Select the Reporting Period", ("Annual", "Quarter")).lower()

col2.title(f"Company Analysis for {ticker}")

# code check
# st.write("current iteration is", ticker, "and", period)

# ticker = str(input("Enter Company Ticker: ")).upper()
# period = str(input("Annual or Quarter: ")).lower()
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

# build a cash flow statement
## CASH FLOW STATEMENT

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
        ROE = net_income / shareholderEquity 
        
        # find price to book ratio (market cap / (total asset - total liability))
        marketCap = enterpriseValue[num]['marketCapitalization'] / 1000
        try:            
            PB = marketCap / (shareholderEquity * 1000)
        except IndexError:
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
        

income_df = createIncomeStatement(income_json)
cashFlow_df = createCashFlowStatement(cashFlow_json)
balanceSheet_df = createBalanceSheet(balance_json)
keyMetrics_df = createKeyRatios(balance_json, income_json,cashFlow_json, enterpriseValue_json)

# display the dataframes
col2.dataframe(income_df)
col2.dataframe(cashFlow_df)
col2.dataframe(balanceSheet_df)
col2.dataframe(keyMetrics_df)