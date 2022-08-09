import re

string='move(,000)'
pattern=re.compile('^move\([0-3],(0\d{2}|1([0-7]\d|80))\)$')
result=pattern.match(string)
print(result.string)