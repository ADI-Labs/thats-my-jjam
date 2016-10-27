from flask import Flask
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def getInfo():
    r = requests.get('http://api.culpa.info/courses/department_id/7')
    return r.text


if __name__ == '__main__':
    app.run()
