import re 

pattern = '^(?:_(\d)(\d)(\d))$'
result=re.match(pattern,'_456')
print(result.groups())