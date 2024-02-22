import schedule
import threading
import time
from flask import Flask, render_template
from modules.server import Server


app = Flask(__name__)
server = Server()

def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(10)

@app.route("/")
def hello():
    if not server.is_connected:
        return render_template('unavailable.html')

    return render_template('index.html', data=server)

@app.route("/report")
def report():
    return render_template('report.html', data=server)

schedule.every(1).minutes.do(server.fetch)

schedule_thread = threading.Thread(target=schedule_run)
schedule_thread.start()

if __name__ == "__main__":
    app.run(debug=True)