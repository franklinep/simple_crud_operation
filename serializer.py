def convert_doc(document) -> dict:
    return {
        "id": str(document["_id"]),
        "name": document["name"],
        "age": document["age"],
    }

def convert_doc_list(documents) -> list:
    return [convert_doc(doc) for doc in documents]