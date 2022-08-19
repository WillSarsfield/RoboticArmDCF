# test script to extract data from excel files
import pandas as pd 

class ExcelInterpreter:
    def __init__(self):
        pass
    
    def get_data(self):
        data_file= pd.read_excel(r'dataset:xlsx')
        print(data_file)
        print(type(data_file))
        data_file.to_csv(r'./dataset.csv',index=None)

interpreter = ExcelInterpreter('').get_data()
