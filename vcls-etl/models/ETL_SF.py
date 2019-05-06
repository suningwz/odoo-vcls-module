from simple_salesforce import Salesforce

class ETL_SF:
    
    __instance = None
    instance = None

    @staticmethod
    def getInstance(userSF, passwordSF, token):
        if ETL_SF.__instance == None:
            ETL_SF(userSF, passwordSF, token)
        return ETL_SF.__instance

    def __init__(self,userSF, passwordSF, token):
        """ Virtually private constructor. """
        if ETL_SF.__instance != None:
            raise Exception("This class is a singleton!")
        else:

            ETL_SF.__instance = self
            ETL_SF.instance = Salesforce(username=userSF, password=passwordSF, security_token=token ,version='41.0')

    def getConnection(self):
        print('Successful connection to Salesforce.')
        return ETL_SF.instance