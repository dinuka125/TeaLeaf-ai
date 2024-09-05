from llama_index.core.tools import BaseTool, FunctionTool 
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import swagger_client
from swagger_client.rest import ApiException
import json
from openai import OpenAI
import pandas as pd

load_dotenv()

serper_api_key = os.getenv("SERP_API_KEY")
browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
news_api = os.getenv("NEWS_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

def search_news(search_input, language='en', limit=3):
    """
    Search and return news 
    """
    url = "https://api.thenewsapi.com/v1/news/all"
    params = {
        'search': search_input,
        'api_token': news_api,
        'language': language,
        'limit': limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch news', 'status_code': response.status_code}

def realtime_weather(location):

    """ Search and Return weather info """

    configuration = swagger_client.Configuration()
    configuration.api_key['key'] = weather_api_key
    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    try:
        api_response = api_instance.realtime_weather(location)
        return api_response
    except ApiException as e:
        return f"Exception when calling APIsApi->Realtime weather: {e}"

def google_search(search_keyword):

    """Search google/web based on search keyword"""

    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_keyword})
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

def summarize_text(objective, text):
    
    client = OpenAI(api_key=openai_api_key)
    prompt = f"Objective: {objective}\nText: {text}\n\nSummarize the above text keeping the objective in mind:"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": "Create a summary according to user's instructions"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def web_scraping(objective, url):
    """ do the webscrapping based on objective and given url"""
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {"url": url}
    data_json = json.dumps(data)
    response = requests.post(f"https://chrome.browserless.io/content?token={browserless_api_key}", headers=headers, data=data_json)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        if len(text) > 10000:
            return summarize_text(objective, text)
        else:
            return text
    else:
        return f"HTTP request failed with status code {response.status_code}"

def search_news(search_input,language='en', limit=3):
    """"
    Call the news api and retreives latest news and return them
    """

    url = "https://api.thenewsapi.com/v1/news/all"
    params = {
        'search':search_input,
        'api_token': "Qa28Lg1e2KEQaaNs49gfJ3uzaAkiZ1bAQt2phnXl",
        'language': language,
        'limit': limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # Return the json response data
    else:
        return {'error': 'Failed to fetch news', 'status_code': response.status_code}

def call_sales_api():
    """
    Call the sales API endpoint and return the sales data
    """
    url = "http://localhost:5000/api/sales"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch sales data', 'status_code': response.status_code}

def call_operations_api():
    """
    Call the operations API endpoint and return the operational data
    """
    url = "http://localhost:5000/api/operations"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch operational data', 'status_code': response.status_code}

def call_dashboard_api():
    """
    Call the dashboard API endpoint and return the combined sales and operational data
    """
    url = "http://localhost:5000/api/dashboard"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch dashboard data', 'status_code': response.status_code}

def load_tea_stock_data():
    """
    Load and return all data from tea stock data CSV file.
    """
    csv_file_path = 'datafiles/tea_stock_data.csv'
    
    if not os.path.exists(csv_file_path):
        return {"error": "Tea stock data CSV file not found"}
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Convert DataFrame to a dictionary
        data = df.to_dict(orient='records')
        
        return data
    except Exception as e:
        return {"error": f"Failed to load tea stock data: {str(e)}"}


