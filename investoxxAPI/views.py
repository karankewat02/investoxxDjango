from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import requests
from sklearn.linear_model import LinearRegression
import datetime
import json

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

API_KEY_LIST = ["mTntCA4FiZkA0GmpM3Gxs8fCfBtbvOos","T7KKLBmDWopzabouJya8JQBeHe5q2Lo5","YRFWLLSLQKHLErOMpT4_IKxZJmA2fUUp","CgxTVaE7tqACpdrTgNuS57MuM6tlw5Vc","g5y8yAWfO77JOw_Bx4GTpbSZeLivXWVS","PNcXk4rdjs8Bvk8x7YC21iSzXHDCMNp3","UgYxlzJuWV2j_JNA6jwrX5Al8Ta2dwIU","o7G7kZIr8vm5FIBQM6215uIwpOEZaLoo","3y3Ni2LAvM7gMhp6SgWvlq9AqXHkBLNC","3y3Ni2LAvM7gMhp6SgWvlq9AqXHkBLNC","ADu65LsibS7Cpf0l_yHmbNNf2YhMZTkz","OcdHW8Khs_l654JLcXWIIjyXWL85m5my","xfJ3Lk3XZIreeed6fySiXSyhVfXgxlrc","OXL5ANG2QlS_3Ec70gSQpxgjwi06hHGx","rXs3qp0O8Kzj2hY4c3TqpavaLpj21YYy"]



def predict_stock_performance(symbol):
    # Get stock data for the last 2 months
    today = datetime.datetime.now().date()
    today = today - datetime.timedelta(days=3)
    two_months_ago = today - datetime.timedelta(days=60)
    api_key = API_KEY_LIST[np.random.randint(0, len(API_KEY_LIST))]
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{two_months_ago}/{today}?adjusted=true&sort=asc&limit=1000&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == "ERROR":
        return "Try again later"
    

    if data['queryCount'] != 0:

        df = pd.DataFrame(data["results"])

        # Calculate RSI
        delta = df['c'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        rs = rs.fillna(method='bfill')
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate EMA
        df['EMA'] = df['c'].ewm(span=14, adjust=False).mean()

        # Use AI to make a prediction
        X = df[['RSI', 'EMA']]
        y = df['c'].shift(-1)
        X = X.iloc[:-1,:]
        y = y.iloc[:-1]


        model = LinearRegression()
        # model = RandomForestRegressor(random_state=0)
        model.fit(X, y)
        future = model.predict(X.iloc[-1:,:])[0]

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        currentPriceURL = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        currentPriceResponse = requests.get(currentPriceURL, headers=headers)
        currentPriceData = currentPriceResponse.json()
        current = currentPriceData["chart"]["result"][0]["indicators"]["quote"][0]["close"][-1]
        dfCurrent = df['c'].iloc[-1]
        priceDiffrece = ((future -dfCurrent) / dfCurrent)*1600
        prediction = current + priceDiffrece
            

        response = {
            'future': future,
            'current': current,
            'prediction': prediction,
            'priceDiffrece': priceDiffrece
        }

        print("Successfull",response)
        return response 
    
    else:
        return "No data found"


def predicted_value(symbol):  
    today = datetime.datetime.now().date()
    today = today - datetime.timedelta(days=3)

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2mo"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['chart']['error']:
        return "Try again later"        

    result = data['chart']['result'][0]
    df = pd.DataFrame(result['indicators']['quote'][0])

    # Calculate RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rs = rs.fillna(method='bfill')
    df['RSI'] = 100 - (100 / (1 + rs))

    # Calculate EMA
    df['EMA'] = df['close'].ewm(span=14, adjust=False).mean()

    # Use AI to make a prediction
    X = df[['RSI', 'EMA']]
    y = df['close'].shift(-1)
    X = X.iloc[:-1,:]
    y = y.iloc[:-1]

    model = RandomForestRegressor(random_state=0)
    # model = LinearRegression()
    model.fit(X, y)
    future = model.predict(X.iloc[-1:,:])[0]
    currentPriceURL = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    currentPriceResponse = requests.get(currentPriceURL, headers=headers)
    currentPriceData = currentPriceResponse.json()
    current = currentPriceData["chart"]["result"][0]["indicators"]["quote"][0]["close"][-1]
    priceDiffrece = (future - current)*8
    prediction = current + priceDiffrece
        
    response = {
        'future': future,
        'current': current,
        'prediction': prediction,
        'priceDiffrece': priceDiffrece
    }
    print("Successfull",response)
    return response
    




# * -----------------------------------------------------------------------------------------------------------------------------------------

@csrf_exempt

def index(request):
    return HttpResponse("Hello, world. You're at the investoxxAPI index.")


@csrf_exempt
def get_data(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        symbol = data['symbol']
        print("request received",symbol)
        # todo prediction = predict_stock_performance(symbol)
        prediction = predicted_value(symbol)
        return JsonResponse({'prediction': prediction})
    else:
        return JsonResponse({'error': 'method not allowed'})

    
@csrf_exempt
def analyze_news(request):
   if request.method == 'POST':
        data = json.loads(request.body)
        news = data['news']
        sid = SentimentIntensityAnalyzer()
        sentiment = sid.polarity_scores(news)
        return JsonResponse({'sentiment': sentiment})
