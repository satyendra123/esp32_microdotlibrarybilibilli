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

3) index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>esp32 relay controller</title>
    <style>
        *{margin: 0;
        padding: 0;}
        button{
            width: 200px;
            height: 200px;
        }
    </style>
</head>
<body>
    <h1>开灯小网页</h1>
    <button class="on">
        开灯
    </button>
    <button class="off">
        关灯
    </button>
    <script>
        const onBtn = document.querySelector(".on");
        const offBtn = document.querySelector(".off");
        onBtn.addEventListener("click",(e)=>{
            fetch("/on",{
                method:"get",
            }).then(e=>{
                console.log("消息",e);
            }).catch(error=>{
                console.log("报错了",error);
            })
        })
        offBtn.addEventListener("click",(e)=>{
            fetch("/off").then(e=>{
                console.log("消息",e);
            }).catch(error=>{
                console.log("报错了",error);
            })
        })
    </script>
</body>
</html>
