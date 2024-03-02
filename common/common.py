import tiktoken
import openai
import os
import requests
import mimetypes
from bs4 import BeautifulSoup
from pathlib import Path
from llama_hub.file.unstructured.base import UnstructuredReader
from app.models.models import db, KnowledgeBase, Log
from llama_index import (
    ServiceContext, set_global_service_context
)
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient


# Load environment variables from .env file
load_dotenv()
# Qdrant vector store
qdrant_client = QdrantClient(
    url=os.environ.get('QDRANT_URL'),
    api_key=os.environ.get('QDRANT_API_KEY'),
)
# Token counter
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
)
callback_manager = CallbackManager([token_counter])
# Openai api key define
api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key
# LLM
llm_openai = OpenAI(model='gpt-3.5-turbo', temperature=0, openai_api_key=api_key)
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0, openai_api_key=api_key)
# Service context
service_context = ServiceContext.from_defaults(
    llm=llm, callback_manager=callback_manager
)
# set the global default!
set_global_service_context(service_context)


mimetypes_list = ['text/plain', 'application/pdf', 'application/msword',
                  'application/vnd.ms-powerpoint', 'text/html', 'message/rfc822',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'application/vnd.openxmlformats-officedocument.presentationml.presentation']

def load_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return {'text': text}
        else:
            return {'error': 'URL is invalid'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
    
def load_file(file):
    mimetype = mimetypes.guess_type(file)
    if mimetype[0] not in mimetypes_list:
        return {'error': 'File is not supported'}
    loader = UnstructuredReader()
    try:
        documents = loader.load_data(file=Path('file/' + file))
    except Exception as msg:
        print(str(msg))
        
        return {'error': 'Unable to load file. Invalid format!'}
    print('LOG LOADING LOADED')
    return {'text': documents[0].text}

def db_logs(db, user_id=None, kb_name=None, status=None, status_info=None, data_object=None, node_id=None, token=None):
    if status == 'success' and data_object == 'knowledge base':
        kb = KnowledgeBase(user_id=user_id, name=kb_name, status=status, node_id=node_id,
                           status_info=status_info + 'Used tokens are ' + str(token))
        db.session.add(kb)
    elif status == 'success':
        data_object.status=status
        data_object.node_id=node_id
        data_object.status_info=status_info + 'Used tokens are ' + str(token)
        db.session.add(data_object)
    elif status == 'error' or data_object == 'log':
        log = Log(user_id=user_id, status=status, status_info=status_info)
        db.session.add(log)
    try:
        db.session.commit()
        return 'Logs submitted'
    except Exception as msg:
        print(msg)
        return 'Error while adding logs'
    