from abc import ABC, abstractmethod
from ETL_SF import *

class ETL(ABC):
    __instance = None
    @staticmethod
    def getInstance():
        if ETL.__instance == None:
            ETL_SF()
        return ETL.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if ETL.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ETL.__instance = self
    @staticmethod
    @abstractmethod
    def getConnection():
        pass