import threading
from dataclasses import dataclass

## Setam Adresele Serverelor
PRODUCER_PORT = 8080
AGGREGATOR_PORT = 8081
CONSUMER_PORT = 8082

## Definim Structura Datelor Trimise
@dataclass
class Task:
    task_id: int
    completion_time: int
    destination: str
## Atribuim valori (set)
    @staticmethod
    def dict2task(d: dict):
        return Task(
            task_id=d['task_id'],
            completion_time=d['completion_time'],
            destination=d['destination']
        )
## Returneaza datele (get)
    def task2dict(self):
        return {
            'task_id': self.task_id, 
            'completion_time': self.completion_time,
            'destination': self.destination
        }

## Cream Task nou
class NextTaskId:
    __current_id = 0
    __lock = threading.Lock()

    @staticmethod
    def next_id():
        with NextTaskId.__lock:
            NextTaskId.__current_id += 1
            return NextTaskId.__current_id
