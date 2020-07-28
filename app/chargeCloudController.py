from base64 import b64encode
from requests.exceptions import ConnectionError
import requests



class ChargeCloudController:

    def __init__(self, env, user, pwd, application, authenticatorid, locationid=None):
        self.env = env
        self.user = user
        self.__pwd = pwd
        self.__application = application
        self.__authenticatorid = authenticatorid
        self.url = "https://" + env + ".chargecloud.de/"
        self.__auth = "context#"
        self.locationid = locationid
        self.location = None
        self.tariff = None

    def checkConnection(self):
        try:
            r = requests.get(url=self.url)
            status = r.status_code
        except ConnectionError:
            status = 500
        return status

    def authorize(self):
        url = self.url + "rest:contract/" + self.__application + "/getContractAuthorizationToken"
        r = requests.get(url=url, auth=("contract#" + self.user, self.__pwd))
        data = "contract#" + r.json()["data"]
        self.__auth = "Token " + str(b64encode(data.encode("utf-8")), "utf-8")

    def getAGB(self):
        url = self.url + "rest:client/" + self.__application + "/getActiveAgb"
        r = requests.get(url=url)
        return r.json()["data"]["text"]

    def getPP(self):
        url = self.url + "rest:client/" + self.__application + "/getActivePrivacyPolicy"
        r = requests.get(url=url)
        return r.json()["data"]["text"]

    def getTariff(self, tariffid):
        if self.tariff is None:
            url = self.url + "emobility:ocpi/" + self.__application + "/ocpi/app/2.0/tariffs/DE/POW/" + tariffid
            headers = {'Authorization': self.__auth}
            r = requests.get(url=url, headers=headers)
            self.tariff = r.json()["data"]
        return self.tariff

    def parseTariff(self, tarifff):
        if tarifff is not None:
            tariff = tarifff[0]
            parsed = dict()
            parsed["id"] = tariff["id"]
            parsed["currency"] = tariff["currency"]
            parsed["time"] = dict()
            el = [None] * (len(tariff["elements"]) - 2)
            parsed["time"]["monday"] = el
            parsed["time"]["tuesday"] = el
            parsed["time"]["wednesday"] = el
            parsed["time"]["thursday"] = el
            parsed["time"]["friday"] = el
            parsed["time"]["saturday"] = el
            parsed["time"]["sunday"] = el
            parsed["time"]["holiday"] = el
            parsed["time"]["always"] = dict()
            for index, element in enumerate(tariff["elements"]):
                comp = element["price_components"][0]
                if comp["type"] == "FLAT":
                    parsed["flat"] = str(comp["price"]).ljust(4, "0").replace(".", ",")
                elif comp["type"] == "ENERGY":
                    parsed["energy"] = str(comp["price"]).ljust(4, "0").replace(".", ",")
                elif comp["type"] == "TIME":
                    if "restrictions" in element:
                        res = element["restrictions"][0]
                        for day in res["day_of_week"]:
                            parsed["time"][day][index - 2] = dict()
                            parsed["time"][day][index - 2]["price"] = str(comp["price"]).ljust(4, "0").replace(".", ",")
                            parsed["time"][day][index - 2]["time"] = res["start_time"] + " - " + res["end_time"]
                            parsed["time"][day][index - 2]["step"] = comp["step_size"]
                            parsed["time"][day][index - 2]["min_duration"] = res["min_duration"]
                    else:
                        parsed["time"]["always"]["price"] = str(comp["price"]).ljust(4, "0").replace(".", ",")
                        parsed["time"]["always"]["step"] = comp["step_size"]
            return parsed

    def getTariffIdByEvseId(self, evseid):
        for cp in self.getChargePoints():
            if cp["id"] == evseid:
                return cp["connectors"][0]["tariff_id"]
        return None

    def getLocation(self):

        # if self.location is not None:
        #     date = zulu.parse(self.location["timestamp"])
        #     if zulu.now().subtract(date) < zulu.parse_delta("5m"):
        #         print("returned chargepoints from cache")
        #         return self.location

        url = self.url + "emobility:ocpi/" + self.__application + "/ocpi/app/2.0/locations/DE/POW/" + self.locationid
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, data=None, headers=headers)
        self.location = r.json()
        print("returned chargepoints")
        return self.location["data"][0]

    def getChargePoints(self):
        return self.getLocation()["evses"]

    def getChargePointsAvailability(self):
        locations = self.getChargePoints()
        for location in locations:
            if location["status"] == "AVAILABLE":
                return True
        return False

    def getControllerAvailability(self):
        locations = self.getChargePoints()
        for location in locations:
            if location["status"] == "UNKNOWN":
                return False
        return True

    def startLoading(self, evseid):
        url = self.url + "rest:contract/" + self.__application + "/startEmobilityTransaction"
        params = {"chargePointEvse": evseid,
                  "authenticatorId": self.__authenticatorid}
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, headers=headers, params=params, data=None)
        # print("Antwort: " + r.text)
        ##debug
        # return self.getTransactionId(evseid)

    #########
    ##DEBUG##
    #########
    def stopLoading(self, transactionId=None):
        url = self.url + "rest:contract/" + self.__application + "/stopEmobilityTransaction"
        params = {"transactionId": transactionId}
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, headers=headers, params=params, data=None)
        return r.text

    def getTransactionId(self, evseid):
        url = self.url + "rest:contract/" + self.__application + "/getEmobilityTransactions"
        headers = {'Authorization': self.__auth}
        params = {"limit": 20,
                  "offset": 0}
        r = requests.get(url=url, headers=headers, params=params)
        records = r.json()["data"]["records"]
        for record in records:
            if record["data"]["evseId"] == evseid:
                return record["id"]
        return None

    def getInvoiceNumber(self):
        # TODO Rechnungsnummer abholen
        return True

    def getInvoicePDF(self):
        # TODO Rechnung mit Rechnungsnummer runterladen, dann hochladen
        return True
