from abc import ABC, abstractmethod


class Capacity(ABC):

    def __init__(self, name: str, energy: int):
        self.name = name
        self.energy = energy

    @abstractmethod
    def execute(self):
        pass