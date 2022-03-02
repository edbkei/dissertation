https://stackoverflow.com/questions/62416577/execute-linux-command-in-python-flask

In a terminal do:
cd ~/test_any/flask/inputdata2

export FLASK_ENV=development
export FLASK_APP=server
flask run --host=0.0.0.0




In another terminal do:
curl localhost:5000/a,b,c. The first argument is:
a = read all, no b and c needed
c = create an token accordingly b, that is the file name.
r = read asset in b.
u = update asset accordindgly to b,that is the file name.
d = delete asset specified in b.
e = checks if exists asset in b.
t = transfer asset pointed in b to new owner in c.


