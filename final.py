import sqlite3
import os
import unittest
import json
import requests
import numpy as np
import scipy.stats
import statistics
import math
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup

# Team Name: Elizabeth + Stella 
# Group Members: Elizabeth Kim and Stella Young 

# Create database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Get DJI Stock API data in json
def stock_api():
    response_API = requests.get('https://api.twelvedata.com/time_series?symbol=DJI&interval=1day&start_date=2021-01-01&end_date=2022-01-01&order=ASC&apikey=e7702bf29d4148cca08ed5c4180e21eb')
    data = response_API.json()
    return data

# Create DJI Stock table
def create_stock_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Stock (date TEXT UNIQUE, stock_open NUMBER, stock_high NUMBER, stock_low NUMBER, stock_close NUMBER)")
    conn.commit()

# Compile DJI Stock API data into database
def add_into_stock_table(cur, conn, add):
    data = stock_api()
    starting = 0 + add
    limit = 25 + add
    data_lst = []
    for i in data['values'][starting:limit]:
        date = i['datetime'][:10]
        start = float(i['open'])
        high = float(i['high'])
        low = float(i['low'])
        close = float(i['close'])
        data_lst.append((date, start, high, low, close))
        for tup in data_lst:
            cur.execute('INSERT OR IGNORE INTO Stock (date, stock_open, stock_high, stock_low, stock_close) VALUES (?,?,?,?,?)', (tup[0], tup[1], tup[2], tup[3], tup[4]))

        conn.commit()

# Get Grammy data in json
def grammy_web():
    web_data = {}
    
    url = "https://en.wikipedia.org/wiki/List_of_American_Grammy_Award_winners_and_nominees"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = soup.find('table')
    row = result.find_all('tr')
    for i in range(1, len(row)):
        for data in row[i].find('td'):
            print(data.text)
            print(row[i].select("td")[1])
            web_data[str(data)] = row[i].select("td")[1].text

    return web_data

# Create Grammy table
def create_grammy_table(data, cur, conn):
    data_key = list(data.keys())
    print(data_key)
    print(data)

    cur.execute("CREATE TABLE Grammy (Artist TEXT PRIMARY KEY, Award_Num INT)")
    for i in data_key:
        cur.execute("INSERT INTO Grammy (Artist, Award_Num) VALUES (?,?)",(i,data[i]))
    conn.commit()


# Join DJI Stock data and Bitcoin data
def join_tables(cur,conn):
    cur.execute("SELECT Stock.date, Bitcoin.bitcoin_close, Stock.stock_close FROM Bitcoin JOIN Stock ON Bitcoin.date = Stock.date")
    results = cur.fetchall()
    conn.commit()
    return results

# Calculate correlation coefficient
def correlation_calc(list_of_tuple):

    bitcoin_list = []
    stock_list = []
    bitcoin_calc = []
    stock_calc = []
    upper_function = []
    bitcoin_calc2 = []
    stock_calc2 = []

    #bitcoin and stock prices in a list
    for date, bitcoin_price, stock_price in list_of_tuple:
        bitcoin_list.append(bitcoin_price)
        stock_list.append(stock_price)

    #bitcoin and stock prices mean
    bitcoin_avg = statistics.mean(bitcoin_list)
    stock_avg = statistics.mean(stock_list)

    #bitcoin and stock prices upper function
    for i in range(len(bitcoin_list)):
        bitcoin_calc.append(bitcoin_list[i] - bitcoin_avg)
        stock_calc.append(stock_list[i] - stock_avg)

    for num1, num2 in zip(bitcoin_calc, stock_calc):
	    upper_function.append(num1 * num2)
        
    upper_final = sum(upper_function)

    #bitcoin and stock prices lower function
    for i in range(len(bitcoin_list)):
        bitcoin_calc2.append((bitcoin_list[i] - bitcoin_avg)**2)
        stock_calc2.append((stock_list[i] - stock_avg)**2)

    lower_function = sum(bitcoin_calc2) 
    lower_function2 = sum(stock_calc2)

    lower_function3 = lower_function*lower_function2

    lower_final = math.sqrt(lower_function3)

    final = upper_final/lower_final
    return final

# Write the correlation coefficient in a file
def write_correlation_calc(filename, correlation):
    with open(filename, "w", newline="") as fileout:
        fileout.write("Correlation between bitcoin price and DJI stock price:\n")
        fileout.write("======================================================\n\n")
        fileout.write(f"The correlation coefficient between bitcoin price and DJI stock price was r = {correlation}.\n")
        fileout.close()

# Create regression line graph
def create_regression_line(list_of_tuple):
    bitcoin_list = []
    stock_list = []

    for date, bitcoin_price, stock_price in list_of_tuple:
        bitcoin_list.append(bitcoin_price)
        stock_list.append(stock_price)

    x = np.array(bitcoin_list)
    y = np.array(stock_list)

    slope, intercept, r, p, stderr = scipy.stats.linregress(bitcoin_list, stock_list)

    line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}'

    fig, ax = plt.subplots()
    plt.title('Bitcoin Price vs DJI Stock Price')
    ax.plot(x, y, linewidth=0, marker='s', label='Data points')
    ax.plot(x, intercept + slope * x, label=line)
    ax.set_xlabel('Bitcoin Price')
    ax.set_ylabel('DJI Stock Price')
    ax.legend(facecolor='white')
    plt.show()

# Create heat map graph
def create_heat_map(list_of_tuple):
    bitcoin_list = []
    stock_list = []

    for date, bitcoin_price, stock_price in list_of_tuple:
        bitcoin_list.append(bitcoin_price)
        stock_list.append(stock_price)

    xy = np.array([bitcoin_list, stock_list])
    corr_matrix = np.corrcoef(xy).round(decimals=2)

    fig, ax = plt.subplots()
    im = ax.imshow(corr_matrix)
    im.set_clim(-1, 1)
    ax.grid(False)
    ax.xaxis.set(ticks=(0, 1), ticklabels=('Bitcoin Price', 'DJI Stock Price'))
    ax.yaxis.set(ticks=(0, 1), ticklabels=('Bitcoin Price', 'DJI Stock Price'))
    ax.set_ylim(1.5, -0.5)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, corr_matrix[i, j], ha='center', va='center', color='r')
    cbar = ax.figure.colorbar(im, ax=ax, format='% .2f')
    plt.show()


def main():
    cur, conn = setUpDatabase("project2.db")
    
    #Creates Bitcoin table 
    create_bitcoin_table(cur, conn)
    cur.execute('SELECT COUNT(*) FROM Bitcoin')
    conn.commit()
    info = cur.fetchall()
    length = info[0][0]
    
    if length < 25:
        add_into_bitcoin_table(cur, conn, 0)
    elif 25 <= length < 50:
        add_into_bitcoin_table(cur, conn, 25)
    elif 50 <= length < 75:
        add_into_bitcoin_table(cur, conn, 50)
    elif 75 <= length < 100:
        add_into_bitcoin_table(cur, conn, 75)
    elif 100 <= length < 125:
        add_into_bitcoin_table(cur, conn, 100)
    elif 125 <= length < 150:
        add_into_bitcoin_table(cur, conn, 125)
    #print(length)
    
    #Creates Stock table
    create_stock_table(cur, conn)
    cur.execute('SELECT COUNT(*) FROM Stock')
    conn.commit()
    length = info[0][0]
    
    if length < 25:
        add_into_stock_table(cur, conn, 0)
    elif 25 <= length < 50:
        add_into_stock_table(cur, conn, 25)
    elif 50 <= length < 75:
        add_into_stock_table(cur, conn, 50)
    elif 75 <= length < 100:
        add_into_stock_table(cur, conn, 75)
    elif 100 <= length < 125:
        add_into_stock_table(cur, conn, 100)
    elif 125 <= length < 150:
        add_into_stock_table(cur, conn, 125)
    #print(length)
    
    #Calculate correlation coefficient
    set_up_calculations = join_tables(cur, conn)
    calculations = correlation_calc(set_up_calculations)
    write_correlation_calc("calculations.txt", calculations)

    #Create Regression line Graph
    create_regression_line(set_up_calculations)

    #Create Heat map Graph
    create_heat_map(set_up_calculations)




if __name__ == "__main__":
    main()