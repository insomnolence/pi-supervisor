from flask import Flask
import threading

app = Flask("supervisor")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def startServer():
    # starts the app server in a thread and returns the thread
    webServer = threading.Thread(name='webServer', target=_startWebServer)
    webServer.setDaemon(True)
    webServer.start()
    return webServer

def _startWebServer():
    app.run()

class Configurator:
    