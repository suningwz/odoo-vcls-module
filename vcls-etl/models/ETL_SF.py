from simple_salesforce import Salesforce
userSF = 'user'
passwordSF = 'password'
token = ''
class ETL_SF:
    __instance = None
    instance = None
    @staticmethod
    def getInstance():
        if ETL_SF.__instance == None:
            ETL_SF()
        return ETL_SF.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if ETL_SF.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ETL_SF.__instance = self
            ETL_SF.instance = 

    def getConnection(self):
        print('Successful connection to Salesforce.')
        return ETL_SF.instance