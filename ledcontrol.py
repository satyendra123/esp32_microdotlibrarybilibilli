#ex-1 control relay
a) lib -> microdot.py （microdot-main\src中）= means lib folder ke andar microdot.py ka file rakhenge hum nikal kar microdot-main folder ke andar src folder hai uske andar file hai waha se nikalkar
b) common ->connect_wifi.py = hum command name se ek folder banayenge aur uske andar connect_wifi.py ka ek file rakhenge
c) public -> index.html = public folder ke andar hum ek file rakhenge index.html file ka
d) main.py

1) connect_wifi.py
from machine import Pin
import time
import network
light = Pin(2,Pin.OUT)
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("...")
    print("...")
    start_time = time.time()
    if not wlan.isconnected():       
        wlan.connect("Xiaomi_A246","zy415415666")
        while not wlan.isconnected():
            light.value(1)
            time.sleep(1)
            light.value(0)
            time.sleep(1)
            if time.time() - start_time > 15:
                print("wifi！！！")
                break
        return False
    else:
        print("wifi！！！！")
        light.value(0)
        print("ip:",wlan.ifconfig())
        return True
​
2) main.py
from lib.microdot import Microdot
from common.connect_wifi import do_connect
from machine import Pin
light = Pin(2,Pin.OUT)
do_connect()
app = Microdot()
@app.get('/on')
def index(request):
    light.value(1)
    return "off"
​
@app.get('/off')
def index(request):
    light.value(0)
    return "on"
app.run(host='0.0.0.0', port=5000, debug=False, ssl=None)

3-a) index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="./style.css">
    <title>ESP32 Relay Control</title>
</head>
<body>
    <h1>Control the LED</h1>
    <button class="on">On</button>
    <button class="off">Off</button>
<script src="./script.js"></script>
</body>
</html>

3-b) style.css
* {
    margin: 0;
    padding: 0;
}

button {
    width: 100px;
    height: 100px;
}

3-c) script.js
const onBtn = document.querySelector(".on");
onBtn.addEventListener("click", (e) => {
    fetch("/on", {
        method: "GET",
    }).then(response => {
        console.log("Response:", response);
    }).catch(error => {
        console.log("Error:", error);
    });
});

const offBtn = document.querySelector(".off");
offBtn.addEventListener("click", (e) => {
    fetch("/off").then(response => {
        console.log("Response:", response);
    }).catch(error => {
        console.log("Error:", error);
    });
});
