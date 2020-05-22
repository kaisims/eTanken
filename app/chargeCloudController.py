from base64 import b64encode

import requests
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
        self.chargepoints = None

    def checkConnection(self):
        r = requests.get(url=self.url)
        return r.status_code

    def checkAvailability(self):
        #TODO Check Verfügbarkeit des Ladepunktes
        return True

    def authorize(self):
        url = self.url + "rest:contract/" + self.__application + "/getContractAuthorizationToken"
        r = requests.get(url=url, auth=("contract#" + self.user, self.__pswd))
        data = "contract#" + r.json()["data"]
        self.__auth = "Token " + str(b64encode(data.encode("utf-8")), "utf-8")
        print(self.__auth)

    def getAGBandPP(self):
        url = self.url + "rest:client/" + self.__application + "/getActiveAgb"
        r = requests.get(url=url)
        text = r.json()["data"]["text"]
        url = self.url + "rest:client/" + self.__application + "/getActivePrivacyPolicy"
        r = requests.get(url=url)
        text += r.json()["data"]["text"]
        print(text)

    def getTarif(self):
        return True

    def getLocation(self):
        url = self.url + "emobility:ocpi/" + self.__application + "/ocpi/app/2.0/locations/DE/*E00003*001/" + self.locationid
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, data=None, headers=headers)
        self.chargepoints = r.json()["data"][0]["evses"]
        print(self.chargepoints)

    def startLoading(self):
        url = self.url + "rest:contract/" + self.__application + "/startEmobilityTransaction"
        params = {"chargePointEvse": self.evseid,
                  "authenticatorId": self.__authenticatorid}
        headers = {'Authorization': self.__auth}
        r = requests.post(url=url, headers=headers, params=params, data=None)
        print("Antwort: " + r.text)
        #TODO transactionID abfragen, um stoppen zu können

    def stopLoading(self):
        url = self.url + "rest:contract/" + self.__application + "/stopEmobilityTransaction"
        transactionId = None
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
