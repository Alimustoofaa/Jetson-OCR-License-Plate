# login as root and run this script via bash & curl:

apt-get update
apt-get upgrade -y
apt install python3-pip

# Install jetson_stats
echo "====================== Installing jetson_stats ======================"
python3 -c "import jtop"
jtop=$?
if [ $jtop == 1]
then
    pip3 install -U jetson-stats
else
    echo "jtop is already"
fi

echo "====================== Installing Pytorch ======================"
apt-get install python3-pip libfreetype6-dev libopenblas-base libopenmpi-dev -y 
apt-get install python3-imaging -y
python3 -c "import torch"
torch=$?
if [ $torch == 1 ]
then
    pip3 install --upgrade setuptools
    pip3 install Cython numpy seaborn tqdm
    wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
    pip3 install torch-1.8.0-cp36-cp36m-linux_aarch64.whl
    rm torch-1.8.0-cp36-cp36m-linux_aarch64.whl
else
    echo "toch is already"
fi

echo "====================== Installing TorchVision ======================"
apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev -y
python3 -c "import torchvision"
torchvision=$?
if [ $torchvision == 1 ]
then
    pip3 install 'pillow<7'
    git clone --branch v0.9.0 https://github.com/pytorch/vision torchvision
    cd torchvision &&
    export BUILD_VERSION=0.9.0 &&
    pip3 install -e .
    rm -r torchvision/
else
    echo "torchvision is already"
fi

echo "================ Upgrade Open-CV ================="
python3 -c "import cv2"
cv2=$?
cv2_version=$(python3 -c "import cv2, sys; sys.exit(float(cv2.__version__[:3]))" 2>&1) 
if [ $cv2 == 1 ] || [[ $cv2_version < 4.5 ]]
then
    wget https://github.com/Qengineering/Install-OpenCV-Jetson-Nano/raw/main/OpenCV-4-5-1.sh
    chmod 755 ./OpenCV-4-5-1.sh
    ./OpenCV-4-5-1.sh
    rm OpenCV-4-5-1.sh
else
    echo "opencv 4.5 is already"
fi

echo "================ Install EasyOCR ================="
python3 -c "import cv2"
easyocr=$?
if [ $easyocr == 1 ]
then
    pip3 install git+git://github.com/jaidedai/easyocr.git --no-deps
else
    echo "EasyOCR is already"
fi

echo "================ Install another Requirements ================="
pip3 install -r requirements.txt

echo "================ Install Arducam ================="
wget https://github.com/ArduCAM/MIPI_Camera/releases/download/v0.0.3/install_full.sh
chmod 755 ./install_full.sh
./install_full.sh -m arducam
rm install_full.sh

sudo reboot
