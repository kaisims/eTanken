from base64 import b64encode

import requests
import zulu
import json


class ChargeCloudController():

    def __init__(self, env, user, pswd, application, authenticatorid, locationid=None):
        self.env = env
        self.user = user
        self.__pswd = pswd
        self.__application = application
        self.__authenticatorid = authenticatorid
        self.url = "https://" + env + ".chargecloud.de/"
        self.__auth = "context#"
        self.locationid = locationid
        self.location = None
        self.tariff = None

    def checkConnection(self):
        r = requests.get(url=self.url)
        return r.status_code

    def authorize(self):
        url = self.url + "rest:contract/" + self.__application + "/getContractAuthorizationToken"
        r = requests.get(url=url, auth=("contract#" + self.user, self.__pswd))
        data = "contract#" + r.json()["data"]
        self.__auth = "Token " + str(b64encode(data.encode("utf-8")), "utf-8")
        print(self.__auth)

    def getAGB(self):
        url = self.url + "rest:client/" + self.__application + "/getActiveAgb"
        r = requests.get(url=url)
        return r.json()["data"]["text"]

    def getPP(self):
        url = self.url + "rest:client/" + self.__application + "/getActivePrivacyPolicy"
        r = requests.get(url=url)
        return r.json()["data"]["text"]

    def getTariff(self, tariffId):
        if self.tariff is not None:
            url = self.url + "emobility:ocpi/" + self.__application + "/ocpi/app/2.0/tarrifs/DE/POW/" + tariffId
            headers = {'Authorization': self.__auth}
            r = requests.post(url=url, data=None, headers=headers)
            self.tariff = r.json()["data"]
        return self.tariff

    def getLocation(self):
        if self.location is not None:
            date = zulu.parse(self.location["timestamp"])
            if zulu.now().subtract(date) < zulu.parse_delta("5m"):
                print("returned chargepoints from cache")
                return self.location
        url = self.url + "emobility:ocpi/" + self.__application + "/ocpi/app/2.0/locations/DE/POW/" + self.locationid
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, data=None, headers=headers)
        self.location = r.json()
        print("returned chargepoints")
        return self.location

    def getChargePoints(self):
        return self.getLocation()["data"][0]["evses"]

    def getChargePointsAvailability(self):
        locations = self.getChargePoints()
        for location in locations:
            if location["status"] == "AVAILABLE":
                return True
        return False

    def startLoading(self, evseid):
        url = self.url + "rest:contract/" + self.__application + "/startEmobilityTransaction"
        params = {"chargePointEvse": evseid,
                  "authenticatorId": self.__authenticatorid}
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, headers=headers, params=params, data=None)
        print("Antwort: " + r.text)
        ##debug
        transId = self.getTransactionId(evseid)
        print("TransId: " + str(transId))

    #########
    ##DEBUG##
    #########
    def stopLoading(self, transactionId = None):
        url = self.url + "rest:contract/" + self.__application + "/stopEmobilityTransaction"
        params = {"transactionId": transactionId}
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, headers=headers, params=params, data=None)
        print("Antwort: " + r.text)

    def getInvoiceNumber(self):
        #TODO Rechnungsnummer abholen
        return True

    def getInvoicePDF(self):
        #TODO Rechnung mit Rechnungsnummer runterladen, dann hochladen
        return True
