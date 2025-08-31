from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <html>
      <head>
        <title>Live Clock</title>
        <script>
          function updateClock() {{
            var now = new Date();
            var dateTimeStr = now.getFullYear() + "-" +
                              ("0" + (now.getMonth()+1)).slice(-2) + "-" +
                              ("0" + now.getDate()).slice(-2) + " " +
                              ("0" + now.getHours()).slice(-2) + ":" +
                              ("0" + now.getMinutes()).slice(-2) + ":" +
                              ("0" + now.getSeconds()).slice(-2);
            document.getElementById("clock").innerHTML = dateTimeStr;
          }}
          setInterval(updateClock, 1000);
        </script>
      </head>
      <body onload="updateClock()">
        <h1>Current Date & Time</h1>
        <p id="clock">{now}</p>
      </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080) # 👈 change port here
