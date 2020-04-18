import gc
import webrepl
import network
import time
webrepl.start()
gc.collect()
network.WLAN(network.AP_IF).active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('UPC4305504', 'zt5nWntck7uk')
count = 0
while not sta_if.isconnected():
    time.sleep_ms(1)
    count += 1
    if count==10000:
        print('Not connected')
        break
print('Config: ', sta_if.ifconfig())
