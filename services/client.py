from doccano_api_client import DoccanoClient

class Client:
    doccano_client = None


def refresh_client():
    Client.doccano_client = DoccanoClient(
        baseurl='http://103.113.81.36:8000/',
        username='admin',
        password='password',
    )
