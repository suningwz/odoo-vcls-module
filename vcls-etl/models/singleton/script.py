from ETL_SF import ETL_SF 
inst = ETL_SF.getInstance()
print(inst)
conn = inst.getConnection()
print(conn)