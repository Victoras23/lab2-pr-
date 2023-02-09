import queue
import threading

import requests
from flask import Flask, request

from settings import AGGREGATOR_PORT, CONSUMER_PORT, PRODUCER_PORT, Task

## Delimitam culorile si definim numarul de lucratori
flask_app = Flask(__name__)
shared_resource = queue.Queue()
NR_OF_WORKERS = 6
OKGREEN = '\033[92m'
ENDC = '\033[0m'

## Receptia taskului
@flask_app.route('/aggregator_task', methods=['POST'])
def post_nest_task():
    json_task = request.get_json()
    task = Task.dict2task(json_task)
    print(f"{OKGREEN}AGGREGATOR: Received {task} from {'PRODUCER' if task.destination == 'consumer' else 'CONSUMER'}{ENDC}")
    shared_resource.put(task)
    return {'status_code': 200}

## Pornim threadurile 
class Worker(threading.Thread):
    def run(self):
        while True:
            task: Task = shared_resource.get()
            if task.destination == 'consumer':
                requests.post(
                    f'http://localhost:{CONSUMER_PORT}/consumer_task', json=task.task2dict())         
            elif task.destination == 'producer':
                requests.post(
                    f'http://localhost:{PRODUCER_PORT}/producer_task', json=task.task2dict())

## Definam lista de threaduri
def run():
    threads: list[threading.Thread] = []

    server_thread = threading.Thread(target=lambda: flask_app.run(
        port=AGGREGATOR_PORT, debug=False, use_reloader=False))
    threads.append(server_thread)

    for _ in range(NR_OF_WORKERS):
        threads.append(Worker())

    for thread in threads:
        thread.start()
