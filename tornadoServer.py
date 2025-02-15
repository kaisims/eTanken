import os
import platform

import pyqrcode
import tornado.ioloop
import tornado.web
import tornado.template
import concurrent.futures
import yaml
from tornado.web import RequestHandler
from app.terminalController import *
from app.chargeCloudController import *

data = dict()
preauth = None


class PreAuth:
    def __init__(self):
        self.evseid = None
        self.thread = None
        self.threadexecutor = None

    def runPreAuth(self):
        self.threadexecutor = concurrent.futures.ThreadPoolExecutor()
        self.thread = self.threadexecutor.submit(tc.preauthorisation)
        return self.thread


class StartHandler(RequestHandler):
    def get(self):

        if tc.checkConnection() and cc.checkConnection() == 200:
            self.render('start.html', url="/chooseChargePoint/")
            print(tc.checkConnection())

        else:
            self.write('Keine Verbindung zur Chargecloud oder des Terminals möglich')


class ChargePointHandler(RequestHandler):
    def get(self):
        cc.authorize()
        chargepoints = cc.getChargePoints()
        for chargepoint in chargepoints:
            chargepoint["url"] = "/showTarif/" + chargepoint["id"]
        if cc.getControllerAvailability():
            self.render('chargepoints.html', chargepoints=chargepoints)
        else:
            self.render('chargepoints.html', chargepoints=None)


class TarifHandler(RequestHandler):
    def get(self, evseid):
        tariff_id = cc.getTariffIdByEvseId(evseid=evseid)
        if tariff_id is not None:
            tariff = cc.getTariff(tariffid=tariff_id)
            parsed = cc.parseTariff(tariff)
            url = "/chooseChargePoint/"
            url2 = "/authorise/" + evseid
            self.render('showTariff.html', evseid=evseid, url=url, url2=url2, tariff=parsed)


class AuthoriseHandler(RequestHandler):
    def get(self, evseid):
        self.render('authorisation.html', url="/abortAuth/", evseid=evseid)
        if tc.checkConnection():
            global preauth
            if preauth is None:
                tc.setupterminal()
                preauth = PreAuth()
                preauth.runPreAuth()
                preauth.evseid = evseid
                print("Authorisation was send to Terminal")
        else:
            print("Send Error")
            self.send_error()

    def options(self, __):
        global preauth
        if isinstance(preauth, PreAuth) and preauth.thread is not None:
            if preauth.thread.done():
                receipt = preauth.thread.result()
                if receipt:
                    cc.startLoading(preauth.evseid)
                    data[receipt] = preauth.evseid
                    print("started Loading, sending Payed " + receipt)
                    self.set_status(200)
                    self.finish(str(receipt))
                    preauth = None
                else:
                    preauth.threadexecutor.shutdown(wait=False)
                    preauth = None
                    print("Send Error - no receipt")
                    self.send_error()
            else:
                print("Terminal still busy")
                self.set_status(204)
                self.finish()


class ChargeHandler(RequestHandler):
    def get(self, receipt):
        self.render('charge.html', receipt=receipt)


class AgbHandler(RequestHandler):
    def get(self):
        self.write(cc.getAGB())


class PPHandler(RequestHandler):
    def get(self):
        self.write(cc.getPP())


class StopTransHandler(RequestHandler):
    def post(self, receipt):
        amount = self.get_argument('amount')
        data["trans"] = dict(amount=amount, receipt=receipt)
        data["ready"] = True
        print("Charge done for " + receipt + " and " + amount)
        self.set_status(200)
        self.finish()

    def get(self, receipt):
        amount = self.get_argument('amount', "500")
        bon = tc.teilstorno(receipt=receipt, amount=int(amount))

        print(cc.stopLoading(cc.getTransactionId(data[receipt])))
        url = "http://localhost:8001/"
        qr = pyqrcode.create(url)
        qr.svg('app/svg/receipt.svg', 5)

        self.render('bon.html', bon=bon, url=url, amount=(1500 - int(amount)))
        del data[receipt]

    def options(self, __):
        x = data.get("ready")
        if not (x is None or x is False):
            print("Send Payment Done Details")
            self.set_status(200)
            self.finish(data["trans"])
            data["trans"] = None
            data["ready"] = False
        else:
            print("Send No Payment Details")
            self.set_status(204)
            self.finish()


def make_app():
    return tornado.web.Application([
        (r"/", StartHandler),
        (r"/chooseChargePoint/", ChargePointHandler),
        (r"/showTarif/([^/]+)?", TarifHandler),
        (r"/authorise/([^/]+)?", AuthoriseHandler),
        (r"/charge/([^/]+)?", ChargeHandler),
        (r"/stopCharge/([^/]+)?", StopTransHandler),
        (r"/getAgb/", AgbHandler),
        (r"/getPP/", PPHandler)
    ], debug=True,
        template_path=os.path.join(dirname, 'app', 'templates'),
        static_path=os.path.join(dirname, 'app')
    )


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    dirname = os.path.dirname(__file__)
    app = make_app()

    try:
        config = yaml.safe_load(open("config.yml"))
    except OSError:
        raise Exception("No config file found")
    app.listen(config["port"])
    tc = TerminalController(**config["terminal"])
    cc = ChargeCloudController(**config["cc"])

    tornado.ioloop.IOLoop.current().start()
