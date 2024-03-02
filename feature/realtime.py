import json
import os
import requests
from common.common import llm, db, Log
from llama_index.llms import OpenAI
from llama_index.tools import FunctionTool
from llama_index.agent import OpenAIAgent


def weather_forecast(city=None, temperature_unit=''):
    """Check current weather and return details in json"""
    if temperature_unit:
        temperature_unit = temperature_unit.lower()
    if temperature_unit == 'fahrenheit':
        unit = 'imperial'
    elif temperature_unit == 'celsius':
        unit = 'metric'
    else:
        unit = ''
    api_key = os.environ.get('WEATHER_API_KEY')
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&&units={unit}&appid={api_key}')
    return response.json()

llm = OpenAI(model='gpt-3.5-turbo-0613', temperature=0, openai_api_key=os.environ.get('OPENAI_API_KEY'))
weather_tool = FunctionTool.from_defaults(fn=weather_forecast)
agent = OpenAIAgent.from_tools([weather_tool], llm=llm, verbose=True)

def realtime_query(query):
    if not query:
        return 'It\s look like you didn\'t ask anything'
    try:
        response = agent.chat(query)
    except Exception as msg:
        print('error = ', str(msg))
        logs = Log(status='error', status_info=str(msg))
        db. session.add(logs)
        db.session.commit()
        return 'Weather API limit exceed. Please after some time.'
    return response.response