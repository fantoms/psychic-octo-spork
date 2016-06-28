#!/bin/bash
sudo systemctl stop serial-getty@ttyS0.service
sudo chmod ugo+rwx /dev/ttyS0

