import os

import endpoint.main as e
from dotenv import load_dotenv

load_dotenv()

a = {
    "vessels": [
        {"imo": "9349667",
         "vessel_name": "ABYAN",
         "gross_tonnage": "75395",
         "type": "Container Ship",
         "year_built": "2008",
         "flag": "Iran (IRN)"}
    ]
}

# def test_main():
#     d = {"imo":"9349667"}
#     r = e.main(d)
#     assert r == a
#
# def test_main_2():
#     d = {"vessel_name":"ABYAN"}
#     r = e.main(d)
#     assert len(r["vessels"]) >= 1

def test_main_3():
    d = {"imo":"9343687", "u_p":  os.environ.get('U_P') }
    r = e.main(d)
    assert len(r["vessels"]) >= 1

def test_main_4():
    d = {"vessel_name":"ABYAN", "u_p":  os.environ.get('U_P') }
    r = e.main(d)
    assert len(r["vessels"]) >= 1