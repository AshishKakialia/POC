Root folder name is POC. Run below commands in POC directory

Create new environment
- python -m venv 'environment_name'

Activate environment command
- source venv/Scripts/activate

Install requirements.txt file command
- pip install -r requirements.txt

NOTE: Before run the below command enter api_key manually at line 24 in python_code/builder.py file.


Run the project command
- python run.py

APIs and Endpoints to get the data. In all APIs, file_name is unique and it is required in everyAPI

Local host link
- http://127.0.0.1:5000/

Endpoints are below
ABBREVIATION: kb - knowledge base
- /train_knowledge_base?data=&kb_name=
data and kb name is required 
it will return 'status' and 'token_usage'
in case of any error it will return 'error'
NOTE: provided data should not be more than 5000 characters

- /update_knowledge_base?data=&kb_name=
data and kb name is required 
it will return 'status' and 'token_usage'
in case of any error it will return 'error'
NOTE: provided data should not be more than 5000 characters

- /insert_knowledge_base?data=&kb_name=
data and kb name is required 
it will return 'status' and 'token_usage'
in case of any error it will return 'error'
NOTE: provided data should not be more than 5000 characters

- /delete_knowledge_base?kb_name=
kb name is required 
it will return 'status'
in case of any error it will return 'error'

- /query_knowledge_base?kb_name=&user_query=&conversation_id=&message_id=
question and kb name is required. Create new conversation instance if conversation_id not given or user sent message first time.
ON EDIT MESSAGE - all parameters required and it will return 'message object' with new conversation instance (new conversation id in message object)
On error it will return object like {'assistant_message':'error_message'} you can show as message

- /get_conversation?conversation_id=
conversation id is required
it will return all previous messages between user and assistant in array of objects like 
{
    'conversations': [
        {
            'id': message.id,
            'conversation_id': conversation_id, 
            'kb_id': kb.id,
            'user_message': user_query,
            'assistant_message': response.response,
            'created_at': message.created_at,
            'updated_at': message.updated_at
        }
    ]
}
in case of any error it will return 'No conversations to load'

- /delete_conversation?conversation_id=
conversation id is required
it will return {'status':'Conversation has been deleted'}
in case of any error it will return {'error':'There is an error. Please try again!'}

- /knowledge_bases
No parameters required.
It will load all knowledge bases created return 
{
    'knowledge_bases': [
        {
            "id": kb.id,
            "name": kb.name,
            "node_id": kb.node_id,
            "status": kb.status.value if kb.status else None,
            "status_info": kb.status_info,
            "created_at": kb.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": kb.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
}