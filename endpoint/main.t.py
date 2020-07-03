import pandas as pd


def main(d):
    imo = d.get("imo")
    vessel_name = d.get("vessel_name")
    names = ["imo", "vessel_name", "gross_tonnage", "type", "year_built", "flag"]
    frame = pd.DataFrame([x.split(',', 5) for x in db.split('\n')[2:]], columns=names)
    resp = {"vessels": []}
    if vessel_name:
        resp["vessels"] = frame[frame['vessel_name'].str.contains(vessel_name)].to_dict("records")
    elif imo:
        resp["vessels"] = frame[frame['imo'].str.contains(imo)].to_dict("records")

    return resp
