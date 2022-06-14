#!/usr/bin/env python3

# note: to this file becomes executable do: chmod +x filename

import sys
sys.path.insert(0, '/home/ubuntu/go/src/github.com/edbkei/fabric-samples/asset-transfer-basic/application-javascript')
from token_manager import t_exists, t_create, t_read, t_update, t_delete, t_exists, t_all, t_transfer

def main():
    arg1=sys.argv[1]
    arg2=""
    arg3=""
    if arg1 != 'h' and arg1 != 'a':
       arg2=sys.argv[2]
    if arg1 == "t":
       arg3=sys.argv[3]
     
    if arg1 == "h":
       print("help")
       print("arg1: commands c(create), r(read), u(update), d(delete), e(exists), a(read all), t(transfer) a token")
       print("arg2: file to option c and u, and asset id for option r, d, and t. Not needed for a. ")
       print("arg3: the transferee in case of t")
    elif arg1 == "c":  # token_create option
       file=open(arg2, "r")
       content=file.read()
       content=content.rstrip()
       print(content)
       a=content.split(",")
       file.close()
       result=t_create(a[0],a[1],a[2],a[3],a[4],a[5])
       print(result)
    elif arg1 == "cc":  # token_create option
       content=arg2
       print("arg2= ", arg2)
       content=content.rstrip()
       print(content)
       a=content.split(",")
       print(sys.argv[2])
       print(sys.argv[3])
       print(sys.argv[4])
       print(sys.argv[5])
       print(sys.argv[6])
       print(sys.argv[7])
       result=t_create(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8])
       print(result)
    elif arg1 == "r":  # token_read option
       result=t_read(arg2)
       print(result)
    elif arg1 == "u":  # token_update option
       file=open(arg2, "r")
       content=file.read()
       content=content.rstrip()
       print(content)
       a=content.split(",")
       file.close()
       result=t_update(a[0],a[1],a[2],a[3],a[4],a[5])
       print(result)
    elif arg1 == "uu":  # token_update option
       content=arg2
       print("arg2= ", arg2)
       content=content.rstrip()
       print(content)
       a=content.split(",")
       result=t_update(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8])
       print(result)
    elif arg1 == "d":  # token_delete option
       result=t_delete(arg2)
       print(result)
    elif arg1 == "e":  # token_exists option
       result=t_exists(arg2)
       print(result)
    elif arg1 == "a":  # token_exists option
       result=t_all()
       print(result)
    elif arg1 == "t":  # token_exists option
       result=t_transfer(arg2,arg3)
       print(result)

    else:
       print("invalid option!")

if __name__ == "__main__":
    main()
