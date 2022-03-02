#!/usr/bin/python
import json
from subprocess import check_output

apps='/home/ubuntu/go/src/github.com/edbkei/fabric-samples/asset-transfer-basic/application-javascript/tokenapp.js'
# check if token exists in ledger
def t_exists(token):
    p = check_output(['node', apps, 'exists',token])
    my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
    start = my_json.find("Result: ") + len("Result: ")
    end = start+5
    substring = my_json[start:end]
    if (substring.find("true")!=-1):
       return True
    else:
       return False

def t_create(asset,finalConsumer,energykwh,status,owner,appraisalvalue,docType):
    p = check_output(['node', apps,'create',asset,finalConsumer,energykwh,status,owner,appraisalvalue,docType])
    return True


def t_read(asset):
    p = check_output(['node', apps,'read',asset])
    my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
    start = my_json.find("Result: ") + len("Result: ")
    end = my_json.rfind("}")
    substring = my_json[start:end]
    substring=substring+"}"
    data = json.loads(substring)
    s=json.dumps(data, indent=4, sort_keys=True)
    return s

def t_update(asset,finalConsumer,energykwh,status,owner,appraisalvalue,docType):
    p = check_output(['node', apps,'update',asset,finalConsumer,energykwh,status,owner,appraisalvalue,docType])
    my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
    start = my_json.find("Result: ") + len("Result: ")
    end = start+15
    substring = my_json[start:end]
    if substring.find("committed")!=-1:
       return True
    else:
       return False

def t_delete(asset):
    check=t_exists(asset)
    if(check):
      p = check_output(['node', apps,'delete',asset])
      my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
      start = my_json.find("Result: ") + len("Result: ")
      end = start+30
      substring = my_json[start:end]
      if (substring.find("Buffer")!=-1):
         return True
      else:
         return False
    else:
      return False

def t_all():
    p = check_output(['node', apps, 'all'])
    my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
    start = my_json.find("Result: ") + len("Result: ")
    end = my_json.rfind("]")
    substring = my_json[start:end]
    substring=substring+"]"
    data = json.loads(substring)
    s=json.dumps(data, indent=4, sort_keys=True)
    return s

def t_transfer(asset,transferee):
    p = check_output(['node', apps,'transfer',asset,transferee])
    #my_json=p.decode('utf8').replace("'", '"') # decode  from bytes to string
    #print(my_json)
    return True



