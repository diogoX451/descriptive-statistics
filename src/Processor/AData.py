from abc import ABC, abstractmethod

class AData(ABC):
    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def set_data(self, data):
        pass

    @abstractmethod
    def get_data_key(self, key):
        pass

    @abstractmethod
    def read(self, file_path):
        pass

    @abstractmethod
    def all_classificators(self):
        pass

    @abstractmethod
    def get_classificator(self, name):
        pass