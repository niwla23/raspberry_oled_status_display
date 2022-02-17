import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import psutil
import time
import requests
import socket

WIDTH = 128 # Width of display
HEIGHT = 64  # Heigth of display
UPDATE_INTERVAL = 5 # data refresh interval in seconds
BURN_IN_PREVENTION_INTERVAL = 600 # shows a white screen every x seconds
PROMETHEUS_BASE_URL = "http://127.0.0.1:9090" # base url for your prometheus server providing alert count

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)


# Clear display.
oled.fill(0)
oled.show()

font_header = ImageFont.truetype("Roboto-Thin.ttf", size=11)
font = ImageFont.truetype("Roboto-Thin.ttf", size=12)

checkmark = Image.open("check.png")
warning_sign = Image.open("warn.png")


def draw_data(hostname: str, ip: str, load1: float, cpu_usage: float, mem_usage: float, temperature: float, alert_count: int, is_ok: bool):
    canvas = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(canvas)

    text_1 = f"{hostname} {ip}"
    text_2 = f"L1: {load1:.1f} CPU: {cpu_usage:.1f}%"
    text_3 = f"Mem.: {mem_usage:.1f}%"
    text_4 = f"Temp.: {temperature:.1f}°C"
    text_5 = f"Firing Alerts: {alert_count}"

    (font_width_1, font_height_1) = font_header.getsize(text_1)
    (font_width_2, font_height_2) = font.getsize(text_2)
    (font_width_3, font_height_3) = font.getsize(text_3)
    (font_width_4, font_height_4) = font.getsize(text_4)

    draw.text(
        (1, 2),
        text_1,
        font=font_header,
        fill=255,
    )

    draw.text(
        (1, font_height_1+4),
        text_2,
        font=font,
        fill=255,
    )

    draw.text(
        (1, font_height_1 + font_height_2 + 2),
        text_3,
        font=font,
        fill=255,
    )

    draw.text(
        (1, font_height_1 + font_height_2 + font_height_3 + 2),
        text_4,
        font=font,
        fill=255,
    )

    draw.text(
        (1, font_height_1 + font_height_2 + font_height_3 + font_height_4 + 1),
        text_5,
        font=font,
        fill=255,
    )

    if is_ok:
        canvas.paste(checkmark, (WIDTH - 45, HEIGHT-32))
    else:
        canvas.paste(warning_sign, (WIDTH - 45, HEIGHT-32))

    # Display image
    oled.image(canvas)

import socket
def get_ip():
    """https://stackoverflow.com/a/28950776"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

counter = 0
while True:
    time_start = time.time()
    if counter >= BURN_IN_PREVENTION_INTERVAL / UPDATE_INTERVAL:
        for i in range(10):
            oled.fill(0)
            oled.show()
            time.sleep(2)
            oled.fill(1)
            oled.show()
            time.sleep(2)
        counter = 0

    is_ok = True

    alerts = requests.get(f'{PROMETHEUS_BASE_URL}/api/v1/query?query=ALERTS{{alertstate="firing"}}')
    alert_count = len(alerts.json()["data"]["result"])
    if alert_count > 0:
        is_ok = False

    load1, _load5, _load15 = psutil.getloadavg()
    hostname=socket.gethostname()

    draw_data(
        hostname=hostname,
        ip=get_ip(),
        cpu_usage=psutil.cpu_percent(0),
        mem_usage=psutil.virtual_memory()[2],
        temperature=psutil.sensors_temperatures()["cpu_thermal"][0].current,
        load1=load1,
        alert_count=alert_count,
        is_ok=is_ok
    )

    oled.show()
    time.sleep(UPDATE_INTERVAL - (time.time() - time_start))
    counter+=1
