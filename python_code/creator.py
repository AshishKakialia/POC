import openai
import os
from python_code.models import *
from common import (
    qdrant_client, service_context, 
    db_logs, token_counter, load_file,
    load_url
)
from llama_index import (
    VectorStoreIndex, Document,
    set_global_service_context
)
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
# Openai api key define
api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key

# set the global default!
set_global_service_context(service_context)

def training_data(data_type=None, kb_name = None, user_id=None, file=None, url=None, text=None):
    logs = []
    result = ''
    if data_type == 'url':
        result = load_url(url)
    elif data_type == 'file':
        result = load_file(file)
    elif data_type == 'text':
        data = text
    if 'error' in result:
        db_logs(db, user_id=user_id, status='error', status_info=result['error'], data_object='log')
        return {'error': result['error']}
    elif 'text' in result:
        data = result['text']
    if kb_name:
        kb_name = kb_name.lower()
    else:
        user = User.query.filter_by(id=user_id).first()
        kb = KnowledgeBase.query.filter_by(user_id=user_id).all()
        kb_name = user.username + 'kb' + str(len(kb) + 1)
    # if len(data) > 5000:
    #     error = 'Data length should not be more than 5000 characters to train knowledge base.'
    #     logs.append({'error': error})
    #     result = db_logs(db, status='error', status_info=error, data_object='log')
    #     print('LOGS status: ', result)
    #     return logs
    print('LOG: Loading data . . .')
    try:
        documents = [Document(text=data)]#loader.load_data(file=Path(file_path))
    except Exception as msg:
        error = 'Data is not loading'
        logs.append({'error': error})
        result = db_logs(db, status='error', status_info=error, data_object='log')
        print('LOGS status: ', result)
        return logs
    node_id = documents[0].doc_id
    token_counter.reset_counts()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=kb_name.capitalize())
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    try:
        print('LOG: Training Data . . .')  
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )
        print('LOG: Data Trained successfully')
        embed = token_counter.total_embedding_token_count
        llm = token_counter.total_llm_token_count
        token_usage = embed + llm
        msg = 'Your knowledge base has been trained with the given data.'
        logs.append({
            'status': msg, 
            'token_usage': token_usage,
        })
        result = db_logs(db, user_id=user_id, kb_name=kb_name, status='success', status_info=msg, node_id=node_id,
                         data_object='knowledge base', token=token_usage)
        return {
            'status': 'Your knowledge base has been trained with the given data.', 
            'token_usage': token_usage,
        }
    except Exception as msg:
        print(msg)
        logs.append({'error': "'Knowledge base not trained, please try again!'"})
        result = db_logs(db, user_id=user_id, status='error', status_info=str(msg), data_object='log')
        print('LOGS status: ', result)
        return logs

def update_data(data_type=None, kb_name = None, user_id=None, file=None, url=None, text=None):
    logs = []
    result = ''
    if data_type == 'url':
        result = load_url(url)
    elif data_type == 'file':
        result = load_file(file)
    elif data_type == 'text':
        data = text
    if 'error' in result:
        db_logs(db, user_id=user_id, status='error', status_info=result['error'], data_object='log')
        return {'error': result['error']}
    elif 'text' in result:
        data = result['text']
    if kb_name:
        kb_name = kb_name.lower()
    kb = KnowledgeBase.query.filter_by(name=kb_name).first()
    # Validate data length
    # if len(data) > 5000:
    #     error = 'Data length should not be more than 5000 characters to train knowledge base.'
    #     logs.append({'error': error})
    #     result = db_logs(db, status='error', status_info=error, data_object='log')
    #     print('LOGS status: ', result)
    #     return logs
    print('LOG: Loading File . . .')
    try:
        documents = [Document(text=data, doc_id=kb.node_id)]
    except Exception as msg:
        error = 'Data is not loading'
        logs.append({'error': error})
        result = db_logs(db, user_id=user_id, status='error', status_info=error, data_object='log')
        print('LOGS status: ', result)
        return logs
    token_counter.reset_counts()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=kb_name.capitalize())
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    try:
        print('LOG: Training Data . . .')
        index = VectorStoreIndex.from_documents(
            [],
            storage_context=storage_context,
        )
        index.update_ref_doc(documents[0], update_kwargs={"delete_kwargs": {'delete_from_docstore': True}})
        print('LOG: Data update successfully')
        embed = token_counter.total_embedding_token_count
        llm = token_counter.total_llm_token_count
        token_usage = embed + llm
        msg = 'Your knowledge base has been updated.'
        logs.append({
            'status': msg,
            'token_usage': token_usage,
        })
        result = db_logs(db, user_id=user_id, status='success', status_info=msg, node_id=kb.node_id,
                         data_object=kb, token=token_usage)
        print('LOGS status: ', result)
        return {
            'status': 'Your knowledge base has been updated.', 
            'token_usage': token_usage,
        }
    except Exception as msg:
        print(msg)
        logs.append({'error': "'Knowledge base not updated, please try again!'"})
        result = db_logs(db, user_id=user_id, status='error', status_info=str(msg), data_object='log')
        print('LOGS status: ', result)
        return logs

def insert_data(data_type=None, kb_name = None, user_id=None, file=None, url=None, text=None):
    logs = []
    result = ''
    if data_type == 'url':
        result = load_url(url)
    elif data_type == 'file':
        result = load_file(file)
    elif data_type == 'text':
        data = text
    if 'error' in result:
        db_logs(db, user_id=user_id, status='error', status_info=result['error'], data_object='log')
        return {'error': result['error']}
    elif 'text' in result:
        data = result['text']
    if kb_name:
        kb_name = kb_name.lower()
    kb = KnowledgeBase.query.filter_by(name=kb_name).first()
    # Characters validation
    # if len(data) > 5000:
    #     error = 'Data length should not be more than 5000 characters to train knowledge base.'
    #     logs.append({'error': error})
    #     result = db_logs(db, user_id=user_id, status='error', status_info=error, data_object='log')
    #     print('LOGS status: ', result)
    #     return logs
    print('LOG: Loading File . . .')
    try:
        documents = [Document(text=data, doc_id=kb.node_id)]
    except Exception as msg:
        error = 'Data is not loading'
        logs.append({'error': error})
        result = db_logs(db, user_id=user_id, status='error', status_info=error, data_object='log')
        print('LOGS status: ', result)
        return logs
    token_counter.reset_counts()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=kb_name.capitalize())
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    try:
        print('LOG: Training Data . . .')  
        index = VectorStoreIndex.from_documents(
            [],
            storage_context=storage_context,
        )
        index.insert(documents[0])
        print('LOG: Data inserted successfully')
        embed = token_counter.total_embedding_token_count
        llm = token_counter.total_llm_token_count
        token_usage = embed + llm
        msg = 'Data has been inserted to knowledge base.'
        logs.append({
            'status': msg, 
            'token_usage': token_usage,
        })
        result = db_logs(db, user_id=user_id, status='success', status_info=msg, node_id=kb.node_id, 
                         data_object=kb, token=token_usage)
        print('LOGS status: ', result)
        return {
            'status': 'Data has been inserted in knowledge base.', 
            'token_usage': token_usage,
        }
    except Exception as msg:
        print(msg)
        logs.append({'error': "'Data has not been inserted in knowledge base, please try again!'"})
        result = db_logs(db, user_id=user_id, status='error', status_info=str(msg), data_object='log')
        print('LOGS status: ', result)
        return logs
