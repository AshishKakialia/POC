from python_code.models import (
    KnowledgeBase, Conversation,
    db, Message
)
from common import (
    qdrant_client, db_logs
)

def delete_conversation(kb_name=None, user_id=None, conversation_id=None):
    if conversation_id and not kb_name:
        try:
            Conversation.query.filter_by(user_id=user_id, id=conversation_id).delete()
            Message.query.filter_by(user_id=user_id, conversation_id=conversation_id).delete()
            db.session.commit()
        except Exception as msg:
            print(msg)
            return {'error':'There is an error. Please try again!'}
        return {'status':'Conversation has been deleted'}
    if kb_name:
        try:
            kb = KnowledgeBase.query.filter_by(user_id=user_id, name=kb_name).first()
            if not kb:
                return {'error': 'No knowledge base to delete conversations'}
            conversations = Conversation.query.filter_by(user_id=user_id, kb_id=kb.id).all()
            if not conversations:
                return {'error': 'No conversations to delete in knowledge base'}
            for conversation in conversations:
                Message.query.filter_by(user_id=user_id, conversation_id=conversation.id).delete()
            Conversation.query.filter_by(user_id=user_id, kb_id=kb.id).delete()
            db.session.commit()
            return {'status':f'All Conversations of knowledge base \'{kb_name}\' has been deleted'}
        except Exception as msg:
            print(msg)
            return {'error': 'Error while deleting conversations. Please try again'}

def delete_data(user_id=None, kb_name=None):
    kb_name = kb_name.lower()
    logs = []
    kb = KnowledgeBase.query.filter_by(user_id=user_id, name=kb_name).first()
    try:
        # Delete conversation
        print('Deleting conversations and messages . . .')
        result = delete_conversation(user_id=user_id, kb_name=kb_name)
        # if 'error' in result:
        #     db_logs(db, status='error', status_info=result['error'], data_object='log')
        #     return result
        print('LOG: ', result['error'])
        print('Deleting Knowledge Base . . .')
        qdrant_client.delete_collection(kb_name.capitalize())
        # Deleting knowledge base
        KnowledgeBase.query.filter_by(user_id=user_id, name=kb_name).delete()
        db.session.commit()
        msg = f"Knowledgebase '{kb_name}' and their respective conversations and messages has been deleted"
        logs.append({kb_name:msg})
        return logs
    except Exception as msg:
        error = str(msg)
        result = db_logs(db, user_id=user_id, status='error', status_info=error, data_object='log')
        print('LOGS status: ', result)
        logs.append({'error':error})
        return logs
    