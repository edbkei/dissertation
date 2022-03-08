https://stackoverflow.com/questions/62416577/execute-linux-command-in-python-flask

In a terminal do:
cd ~/ledgerserver

export FLASK_ENV=development
export FLASK_APP=server
flask run --host=0.0.0.0




In another terminal do:
curl localhost:5000/a,b,c,d,f,g,h. The first argument (a) is the command symbol. The rest (b-j) is the parameters.
a  = read all. No other parameter is needed.
c  = create an token accordingly b, that is the file name. No other parameter is needed.
cc = create an token with b=asset, c=finalConsumer, d=energyKWH, e=status, f=owner, g=appraisedValue, h=docType
r  = read asset in b. No other parameter is needed.
u  = update token data accordindgly to b,that is the file name. No other parameter is needed.
uu = update token data with b=asset, c=finalConsumer, d=energyKWH, e=status, f=owner, g=appraisedValue, h=docType
d  = delete token specified in b. No other parameter is needed.
e  = checks if exists asset in b. No other parameter is needed.
t  = transfer asset pointed in b to new owner in c. No other parameter is needed.


