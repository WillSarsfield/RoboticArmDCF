import re

string='pump(4,4000)'
pattern=re.compile('^pump\([0-9]+,[0-9]+\)$')
result=pattern.match(string)
print(result.string)