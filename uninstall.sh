#!/bin/bash


# Remove service
echo "Eliminando el servicio..."
sudo systemctl stop pathanalisys.service
sudo systemctl disable pathanalisys.service
sudo rm /etc/systemd/system/pathanalisys.service