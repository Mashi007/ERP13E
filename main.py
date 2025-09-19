# main.py mínimo funcional para Railway
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "ERP13 Enterprise - Sistema en construcción"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
