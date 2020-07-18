import requests
import json
from FroniusConnector import FroniusConnector
from datetime import datetime, timedelta
import pandas as pd
from os import path


def fetch_api(req):
    r = requests.get(req[0], params=req[1])
    return r.text


def save_json(res, timestamp):
    with open("./json_response/" + timestamp + ".json", 'w') as f:
        f.write(res)


def parse_json_res(res, tkey="EnergyReal_WAC_Sum_Produced"):
    def find_key_recursive(val, target_key, cur_key=""):
        if cur_key == target_key:
            return val
        if type(val) == dict:
            for onekey in val:
                content = val[onekey]
                return find_key_recursive(content, target_key, onekey)

    res_dict = json.loads(res)
    timestamp = res_dict["Head"]["Timestamp"].replace(":", ".")
    save_json(res, timestamp)
    status_code = res_dict["Head"]["Status"]["Code"]
    if status_code != 0:
        raise Exception("Bad Response from Inverter:", status_code, res_dict)
    target_content = find_key_recursive(
        res_dict, tkey)
    date_content = res_dict["Head"]["RequestArguments"]["StartDate"]
    start_date = datetime.fromisoformat(date_content)
    return target_content, start_date, timestamp


def get_start_end_date(day_offset=14):
    def get_day_month_year(date_obj):
        day, month, year = date_obj.strftime("%d.%m.%Y").split(".")
        return int(day), int(month), int(year)

    now_date = get_day_month_year(datetime.now())
    start_date = get_day_month_year(
        datetime.today() - timedelta(days=day_offset))

    return "{}.{}.{}".format(*start_date), "{}.{}.{}".format(*now_date)


def parse_target_content(content, start_date, tkey="EnergyReal_WAC_Sum_Produced"):

    unit = content['Unit']
    col_head = "{}({})".format(tkey, unit)
    vals = content['Values']

    res_list = []
    for sec_offset in vals:
        energy = vals[sec_offset]
        timestamp = (start_date + timedelta(seconds=int(sec_offset))
                     ).strftime("%d/%m/%Y %H:%M:%S")
        res_list.append((timestamp, energy))

    res_df = pd.DataFrame(
        res_list, columns=["timestamp", col_head])
    res_df.set_index("timestamp", inplace=True)
    res_df.sort_values(by="timestamp", inplace=True)
    return res_df


def save_csv(fname, newdf):
    fpath = "./csv_output/" + fname
    newdf.to_csv(fpath, index=True)


def request_produce_data(series_type):
    start, end = get_start_end_date()
    fc = FroniusConnector('192.168.50.200')
    req = fc.request_historic_data(
        start, end, series_type)  # DailySum or Detail
    res = fetch_api(req)
    target_content, start_date, timestamp = parse_json_res(res)
    newdf = parse_target_content(target_content, start_date)
    save_csv("{}_{}.csv".format(series_type, timestamp), newdf)

request_produce_data("DailySum")
request_produce_data("Detail")