#!/bin/bash


# Install python3.11
if ! command -v python3.11 &> /dev/null
then
      wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tar.xz
      tar -xf Python-3.11.5.tar.xz
      cd Python-3.11.5
      ./configure --enable-optimizations
      make -j `nproc`
      sudo make altinstall
else
    echo "Python 3.11 ya está instalado."
fi

if ! python3.11 -m pip &> /dev/null
then
      wget https://bootstrap.pypa.io/get-pip.py
      sudo python3.11 get-pip.py
else
    echo "Pip 3.11 ya está instalado."
fi


# Install python3 dependencies
sudo apt-get install python3
sudo python3.11 -m pip install -r requirements.txt


# Create service
DIR="service"
# Verificar si el directorio ya existe
if [ ! -d "$DIR" ]; then
    mkdir "$DIR"
fi
touch ./service/pathanalisys.service
echo "[Unit]" > ./service/pathanalisys.service
echo "Description=Pathanalisys service" >> ./service/pathanalisys.service
# echo "After=network.target" >> ./service/pathanalisys.service
echo "" >> ./service/pathanalisys.service
echo "[Service]" >> ./service/pathanalisys.service


# executable path
APP_NAME="pathanalisys"
mv ./main.py ./$APP_NAME
chmod +x ./$APP_NAME
CURRENT_DIR=$(pwd)
PATHANALISYS_PATH="$CURRENT_DIR/$APP_NAME"
PYTHON_PATH=$(which python3.11)
echo "ExecStart=$PYTHON_PATH $PATHANALISYS_PATH" >> ./service/pathanalisys.service
echo "" >> ./service/pathanalisys.service
echo "[Install]" >> ./service/pathanalisys.service
echo "WantedBy=multi-user.target" >> ./service/pathanalisys.service


# Configure the service in systemd
echo "Configurando el servicio en systemd..."
sudo cp ./service/pathanalisys.service /etc/systemd/system/pathanalisys.service
sudo systemctl daemon-reload
sudo systemctl enable pathanalisys.service
sudo systemctl daemon-reload
sudo systemctl start pathanalisys.service
sudo systemctl status pathanalisys.service

