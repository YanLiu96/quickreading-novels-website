import aiocache
import os
import sys

from sanic import Sanic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.views import api_bp
from src.views import novels_bp
from src.config import  CONFIG
from src.views import operate_bp

app = Sanic(__name__)
app.blueprint(api_bp)
app.blueprint(novels_bp)
app.blueprint(operate_bp)
if __name__ == "__main__":
    app.run(host="0.0.0.0", workers=2, port=8001, debug=CONFIG.DEBUG)
