# DoA-Measurement-FlowChart![201201225_338368707695422_8014146077723186862_n](https://user-images.githubusercontent.com/86065919/122541662-79904a00-d05c-11eb-8951-282c7f9b7247.jpg)

ckeck which is the RPi default receiver
```bash
sudo iw dev
```

specifying target Wi-Fi freqency
![Wi-Fi band pic](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/2.4_GHz_Wi-Fi_channels_%28802.11b%2Cg_WLAN%29.svg/660px-2.4_GHz_Wi-Fi_channels_%28802.11b%2Cg_WLAN%29.svg.png)


# RPI:
## to draw a new ground_truth.csv
```bash
sudo python /altered/RPI_makegroundtruth.py
```
## to test whether servomotor works
```bash
sudo python /altered/testcode/RPI_servotest.py
```
## to start transmitting data
```bash
sudo python /altered/RPI_main.py
```
*** need to change the target wi-fi name!! ***

## other file explaination
gura.py : lib for RPI_main.py
( including GetChannel.py, GetInterface.py, GetSignal.py )

# COM:
## to receive data and compute (main code)
```bash
sudo python /altered/COM_main.py
```
## to visualize ground truth
```bash
sudo python /altered/plot_ground_truth.py
```
*** need to change the path of ground_truth file!! ***

## other file explaination
lib_algo.py : lib for COM_main.py