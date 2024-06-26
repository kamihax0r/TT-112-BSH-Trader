import requests
from session_manager import SessionManager

def test_connection():
    session_manager = SessionManager()
    session_manager.create_session()
    headers = session_manager.get_headers()

    url = f'{session_manager.BASE_URL}/sessions/validate'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
