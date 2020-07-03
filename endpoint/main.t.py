import pandas as pd

def main(d):
    unlocode = d.get("unlocode")
    terminal_code = d.get("terminal_code")
    names = ["unlocode","alternative","terminal_code",
             "terminal_facility_name","terminal_company_name",
             "latitude","longitude","last_change",
             "valid_from","valid_until","terminal_website",
             "terminal_address","remarks"]
    frame = pd.DataFrame([x.split(',',12) for x in db.split('\n')[2:]],columns=names)
    resp = {"locations":[]}
    if unlocode:
        resp["locations"] = frame[frame["unlocode"]==unlocode].to_dict("records")
    elif terminal_code:
        resp["locations"] =   frame[frame["terminal_code"]==terminal_code].to_dict("records")

    return resp