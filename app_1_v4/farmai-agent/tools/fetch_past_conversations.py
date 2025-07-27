import os

from google.cloud import firestore

project_id = os.getenv("PROJECT_ID")
db = firestore.Client(project=project_id)

def get_last_5_conversations(userid:str) -> dict:
    """
    Retrieves the past five conversations of the farmer.

    Args:
        userid (str): user id of the user

    Returns:
        dict: past 5 conversations
    """

    try:

        query = db.collection('conversations').where(filter=('user_id', '==', int(userid)))

        docs = query.stream()

        conversations = []
        for doc in docs:
            data = doc.to_dict()
            conversations.append(data)

        print("conversations fetched: ")
        return {"conversations": conversations}
    except Exception as e:
        return {}


# get_last_5_conversations("846240145")