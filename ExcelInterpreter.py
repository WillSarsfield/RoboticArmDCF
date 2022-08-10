# test script to extract data from excel files
import pandas as pd 
data_file = pd.read_excel(r'dataset.xlsx')
print(data_file)
data_file.to_csv(r'./dataset.csv',index=None,header=True)

class ExcelInterpreter:
    def __init__(self,filename):
        self.filename=filename
    
    def get_data(self):
        data_file= pd.read_excel(r'dataset:xlsx')
        print(data_file)
        data_file.to_csv(r'./dataset.csv',index=None,header=False)
