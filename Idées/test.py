# Tutorial I followed : https://youtu.be/NnE1KVhSyzw

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
plt.style.use('seaborn')

import yfinance as yf
msft = yf.Ticker('msft')

stockinfo = msft.info

# for key,value in stockinfo.items():
#     print(key,':',value)

print(msft.sustainability)
# ESG Values are : environmentScore, governanceScore and socialScore
# The sum of these values is : totalEsg
# esgPerformance is self-explanatory

print(msft.recommendations)
# Shows professionals recommendations in chronological order

# df = msft.dividends
# data = df.resample('Y').sum()
# data = data.reset_index()
# data['Year'] = data['Date'].dt.year

# plt.figure()
# plt.bar(data['Year'], data['Dividends'])
# plt.ylabel('Dividend Yield')
# plt.xlabel('Year')
# plt.title('Microsoft Dividend History')
# plt.xlim(2002,2020)
# plt.show()

#    ^ Shows the last dividends of the company

print(msft.cashflow)
print(msft.financials)
print(msft.balance_sheet)

# Return various data

today = datetime.now().date().strftime('%Y-%m-%d')
dataframe = msft.history(start='2000-01-01', end=today)

plt.figure()
plt.plot(dataframe['Close'])
plt.show()

