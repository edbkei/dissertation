#!/usr/bin/python
import json
from subprocess import check_output
p = check_output(['node', 'tokenapp.js', 'exists','asset31'])
my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
print(my_json)
start = my_json.find("Result: ") + len("Result: ")
end = start+5
substring = my_json[start:end]
print(substring)

