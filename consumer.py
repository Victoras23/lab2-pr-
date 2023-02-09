import time
import queue
import threading

import requests
from flask import Flask, request

from settings import CONSUMER_PORT, AGGREGATOR_PORT, Task

## Delimitarea culorilor si numarul de lucratori  
flask_app = Flask(__name__)
shared_resource = queue.Queue()
OKBLUE = '\033[94m'
ENDC = '\033[0m'
NR_OF_WORKERS = 6

## Receptia taskurilor
@flask_app.route('/consumer_task', methods=['POST'])
def consumer_task():
    json_task = request.get_json()
    task = Task.dict2task(json_task)
    print(f'{OKBLUE}CONSUMER: Received {task} from AGGREGATOR{ENDC}')
    shared_resource.put(task)
    return {'status_code': 200}

## Pornim Threadurile
class Worker(threading.Thread):
    def run(self):
        while True:
            task: Task = shared_resource.get()
            time.sleep(task.completion_time)
            task.destination = 'producer'
            requests.post(f'http://localhost:{AGGREGATOR_PORT}/aggregator_task', json=task.task2dict())

## Definim lista de Threaduri
def run():
    threads: list[threading.Thread] = []

    server_thread = threading.Thread(target=lambda: flask_app.run(
        port=CONSUMER_PORT, debug=False, use_reloader=False))
    threads.append(server_thread)

    for _ in range(NR_OF_WORKERS):
        threads.append(Worker())

    for thread in threads:
        thread.start()
