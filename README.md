# Raspberry Pi Mini OLED Status Display
Use a SSD1306 128x64 OLED Display connected over I2C to show system info about your Raspberry Pi.

It shows CPU Usage, Load, Memory Usage, CPU Temperature and number of firing alerts from your prometheus cluster. The icon on the right is a checkmark if there are no alerts firing. Except there is a warning sign.

![Image](docs/image.jpg)

## Setup
 - enable I2C in raspi-config
 - plug in your display to the I2C pins
 - clone this repo
 - run `pip3 install -r requirements.txt`
 - adjust the settings at the top of main.py
 - copy the service file to /etc/systemd/system
 - run `sudo systemctl enable --now` to enable and start the service.