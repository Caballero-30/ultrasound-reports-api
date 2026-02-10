from google.cloud import firestore

_firestore_client: firestore.Client | None = None


def get_firestore_client() -> firestore.Client:
    global _firestore_client

    if _firestore_client is None:
        _firestore_client = firestore.Client()

    return _firestore_client
