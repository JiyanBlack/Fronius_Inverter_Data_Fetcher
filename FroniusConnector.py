import requests
import json


class FroniusConnector:
    '''
    Connector connects Fronius Inverter API v1 to Python Objects
    '''

    def __init__(self, ipaddress):
        self.ip = ipaddress  # LAN IP address of Fronius Inverter

    def request_api_version(self):
        return "http://{}/solar_api/GetAPIVersion.cgi".format(self.ip), {}

    def request_get_system_realtime_data(self):
        return "http://{}/solar_api/v1/GetInverterRealtimeData.cgi".format(self.ip), {"Scope": "System"}

    def request_logger_data(self):
        return "http://{}/solar_api/v1/GetLoggerInfo.cgi".format(self.ip), {}

    def request_historic_data(self, start, end, series_type):
        print("Fetch {} data of EnergyReal_WAC_Sum_Produced for date period {} to {}".format(series_type, start,end))
        return ("http://{}/solar_api/v1/GetArchiveData.cgi".format(self.ip),
                {"Scope": "System", "SeriesType": series_type, "StartDate": start, "EndDate": end, "Channel": "EnergyReal_WAC_Sum_Produced"})
