#!/bin/sh

# Deploys the pi-watcher to a raspberry pi

ansible-playbook -b -u pi ./ansible/playbook.yml -i ./ansible/hosts
