# OCR License Plate Indonesia


## Installation Requirement for Jetson Nano

### PyTorch
- PyTorch 1.8.0
```bash
$wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
$sudo apt-get install python3-pip libopenblas-base libopenmpi-dev 
$pip3 install Cython
$pip3 install numpy torch-1.8.0-cp36-cp36m-linux_aarch64.whl
```

### TorchVision
- TorchVision v0.9.0
```bash
$apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev -y
$pip3 install 'pillow<7'
$git clone --branch v0.9.0 https://github.com/pytorch/vision torchvision
$cd torchvision &&
$export BUILD_VERSION=0.9.0 &&
$python3 setup.py install --user
$rm -r torchvision/
```

### Upgrade OpenCV
- OpenCV 4.5.1
```bash
$wget https://github.com/Qengineering/Install-OpenCV-Jetson-Nano/raw/main/OpenCV-4-5-1.sh
$sudo chmod 755 ./OpenCV-4-5-1.sh
$./OpenCV-4-5-1.sh
$rm OpenCV-4-5-1.sh
```
### install with shell
```bash
$sudo su
$chmod chmod +x setup.sh
$./setup.sh
```

## Test Camera
```bash
$gst-launch-1.0 v4l2src device="/dev/video0" ! "video/x-raw, width=1280, height=720, framerate=30/1, format=(string)UYVY" ! nvvidconv ! 'video/x-raw(memory:NVMM), format=(string)I420' ! omxh264enc control-rate=1 bitrate=500000 ! qtmux ! filesink location=test.mp4 -e
```