import subprocess
import csv
from flask_httpauth import HTTPTokenAuth
from werkzeug.utils import secure_filename



from flask import Flask, abort
app = Flask(__name__)
app.secret_key = "my secret key"
auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    "secret-token-1": "operator",
    "secret-token-2": "user"
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

def run_command(command):
    reader=csv.reader(command.split('\n'), delimiter=',')
    array=[]
    for row in reader:
        array.append(row)
        print(row)
    #print (array[0][0], array[0][1], array[0][2])
    option=array[0][0]
    #print (option)
    user=auth.current_user()
    flag=0

    if option=="a":
       flag=1
       command="./do.py "+array[0][0]
    elif (option=="c" and user=="operator"):
       print("creating ...")
       flag=1
       command="./do.py c "+array[0][1]
    elif (option=="cc" and user=="operator"):
       print("creating ...")
       flag=1
       command="./do.py cc "+array[0][1]+" "+array[0][2]+" "+array[0][3]+" "+array[0][4]+" "+array[0][5]+" "+array[0][6]+" "+array[0][7]
    elif option=="r":
       print("reading ...")
       flag=1
       command="./do.py r "+array[0][1]
    elif (option=="u" and user=="operator"):
       print("updating ...")
       flag=1
       command="./do.py u "+array[0][1]
    elif (option=="uu"):
       print("updating...")
       flag=1
       command="./do.py uu "+array[0][1]+" "+array[0][2]+" "+array[0][3]+" "+array[0][4]+" "+array[0][5]+" "+array[0][6]+" "+array[0][7]
    elif (option=="d" and user=="operator"):
       flag=1
       print("deleting ...")
       command="./do.py d "+array[0][1]
    elif option=="e":
       print("checking if exists ...")
       flag=1
       command="./do.py e "+array[0][1]
    elif option=="t":
       print("transferring ...")
       flag=1
       aux=array[0][2]
       print(aux)
       command="./do.py t "+array[0][1]+" "+aux
       print(command)
    else:
      print("wrong input data")
    if (flag==1):
       return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    else:
       abort(404)

@app.route('/<command>')
@auth.login_required
def command_server(command):
    print("Hello, {}!".format(auth.current_user()))
    return run_command(command)

if __name__ == "__main__":
     app.run(debug=True ,port=5000,use_reloader=False)
