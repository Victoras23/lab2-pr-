import time
import random
import threading

import requests
from flask import Flask, request

from settings import PRODUCER_PORT, AGGREGATOR_PORT, NextTaskId, Task

## Definim numarul de lucratori si delimitim prin culori serverul
flask_app = Flask(__name__)
FAIL = '\033[91m'
ENDC = '\033[0m'
NR_OF_WORKERS = 6

## Primim taskul inapoi
@flask_app.route('/producer_task', methods=['POST'])
def producer_task():
    json_task = request.get_json()
    task = Task.dict2task(json_task)
    print(f'{FAIL}PRODUCER: Received {task} from AGGREGATOR{ENDC}')
    return {'status_code': 200}

## Pornim threadurilor
class Worker(threading.Thread):
    def run(self):
        while True:
            task = Task(task_id=NextTaskId.next_id(), completion_time=random.randint(1, 3), destination='consumer')
            requests.post(
                f'http://localhost:{AGGREGATOR_PORT}/aggregator_task', json=task.task2dict())
            
            time.sleep(random.choice([0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]))

## Cream insusi Threadurile
def run():
    threads: list[threading.Thread] = []

    server_thread = threading.Thread(target=lambda: flask_app.run(
        port=PRODUCER_PORT, debug=False, use_reloader=False))
    threads.append(server_thread)

    for _ in range(NR_OF_WORKERS):
        threads.append(Worker())

    for thread in threads:
        thread.start()
