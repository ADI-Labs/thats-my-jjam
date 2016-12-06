import json

def test_index(app):
    response = app.get("/")
    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["status"] == "success"
