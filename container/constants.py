import os
import requests

DEFAULT_NOTEBOOK_DIR_PATH = "work/scripts/"
JUPYTER_RUNTIME_DIR = f"{os.getenv('HOME')}/.local/share/jupyter/runtime"
HOST_PORT = 8888

def set_host_ip():
    try:
        requests.get(f"http://host.docker.internal:{HOST_PORT}")
        return "host.docker.internal"
    except requests.ConnectionError as e:
        return "172.17.0.1"

HOST_IP = set_host_ip()
if not HOST_IP:
    raise Exception("HOST IP not set")