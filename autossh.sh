#!/bin/bash
#autossh -M 56400 -f -N -o "PubkeyAuthentication=yes" -o "PasswordAuthentication=no" -i /home/chip/.ssh/id_rsa -R 43200:localhost:22 -L 9092:127.0.0.1:9092 user@host &
#good autossh -M 56400 -f -N -o "PubkeyAuthentication=yes" -o "PasswordAuthentication=no" -i /home/chip/.ssh/id_rsa -R 43200:localhost:22 -L 9092:localhost:9092 user@host &
#GREAT autossh -M 56400 -f -N -o "PubkeyAuthentication=yes" -o "PasswordAuthentication=no" -i /home/chip/.ssh/id_rsa -R 43200:localhost:22 -L 9092:localhost:9092 user@host &
#testing new options:
autossh -M 56400 -f -N -o "PubkeyAuthentication=yes" -o "PasswordAuthentication=no" -o "ServerAliveInterval 5" -o "ServerAliveCountMax 2" -i /home/chip/.ssh/id_rsa -R 43200:localhost:22 -L 9092:localhost:9092 user@host &

exit 0
