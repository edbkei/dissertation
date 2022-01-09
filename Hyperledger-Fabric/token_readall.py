#!/usr/bin/python
import json
from subprocess import check_output
p = check_output(['node', 'tokenapp.js', 'all'])
my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
start = my_json.find("Result: ") + len("Result: ")
end = my_json.rfind("]")
substring = my_json[start:end]
substring=substring+"]"
data = json.loads(substring)
s=json.dumps(data, indent=4, sort_keys=True)
print(s)

