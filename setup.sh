# login as root and run this script via bash & curl:

apt-get update
apt-get upgrade -y
apt install python3-pip

# Install jetson_stats
echo "====================== Installing jetson_stats ======================"
pip3 install -U jetson-stats

echo "====================== Installing Pytorch ======================"
apt-get install python3-pip libopenblas-base libopenmpi-dev -y
pip3 install Cython numpy
wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
pip3 install torch-1.8.0-cp36-cp36m-linux_aarch64.whl
rm torch-1.8.0-cp36-cp36m-linux_aarch64.whl

echo "====================== Installing TorchVision ======================"
apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev -y
pip3 install 'pillow<7'
git clone --branch v0.9.0 https://github.com/pytorch/vision torchvision
cd torchvision &&
export BUILD_VERSION=0.9.0 &&
python3 setup.py install --user
rm -r torchvision/

echo "================ Upgrade Open-CV ================="
wget https://github.com/Qengineering/Install-OpenCV-Jetson-Nano/raw/main/OpenCV-4-5-1.sh
chmod 755 ./OpenCV-4-5-1.sh
./OpenCV-4-5-1.sh
rm OpenCV-4-5-1.sh