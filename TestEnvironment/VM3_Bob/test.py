
req_attrs=[]

req_attrs.append({"name": "degree", "restrictions": [{"schema_name": "degree schema"}],})
print(req_attrs)
#birth_date = datetime.date(d.year - age, d.month, d.day)
birth_date_format="%Yn%d"
print(birth_date_format)
import datetime
d = datetime.date.today()
age=18
birth_date = datetime.date(d.year - age, d.month, d.day)
birthdate_dateint=birth_date.strftime(birth_date_format)
print(birthdate_dateint)

req_preds=[{"name": "birthdate_dateint", "p_type": "<=", "p_value": birth_date.strftime(birth_date_format), "restriction": [{"schema_name": "degree schema"}],}]
#print(f"0_{req_attr['name']}_uuid")

for req_attr in req_attrs:
    #print(req_attr)
    print(f"0_{req_attr['name']}_uuid")

for req_pred in req_preds:
    print(f"0_{req_pred['name']}_GE_uuid")
