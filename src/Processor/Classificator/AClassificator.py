from abc import ABC, abstractmethod

class AClassificator(ABC):
    @abstractmethod
    def classify(self, data):
        pass