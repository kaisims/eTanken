import os
import platform
import time
from abc import ABC

import tornado.ioloop
import tornado.web
import tornado.template
import concurrent.futures

from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler

import asyncio
from app.terminalController import *
from app.chargeCloudController import *

data = dict(paid=False)
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
            cc.authorize()
            print(tc.checkConnection())
            cc.getLocation()
        else:
            self.write('Hmm kein Terminal zu finden')


class ChargePointHandler(RequestHandler):
    def get(self):
        chargepoints = cc.getChargePoints()
        for chargepoint in chargepoints:
            chargepoint["url"] = "/showTarif/" + chargepoint["id"]
        self.render('chargepoints.html', chargepoints=chargepoints)


class TarifHandler(RequestHandler):
    def get(self, evseid):

        url = "/authorise/" + evseid
        self.render('showTarif.html', evseid=evseid, url=url, euro=12)


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
            self.send_error()

    def options(self, __):
        global preauth
        if preauth.thread is not None and preauth.thread.done():
            receipt = preauth.thread.result()
            if receipt:
                cc.startLoading(preauth.evseid)
                data[receipt] = preauth.evseid
                print("started Loading, sending Payed " + receipt)
                self.set_status(200)
                self.finish(str(receipt))
            else:
                self.send_error()
            preauth.threadexecutor.shutdown(wait=False)
            preauth = None
        else:
            print("Terminal still busy")
            self.set_status(204)
            self.finish()


class AbortHandler(RequestHandler):
    def get(self):
        global preauth
        preauth.threadexecutor.shutdown(wait=False)
        preauth = None
        #Geht nicht
        tc.abort()
        self.redirect('/chooseChargePoint/', permanent=False)


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
        tc.teilstorno(receipt=receipt, amount=amount)
        self.set_status(200)
        self.finish()

    #DEBUG Function
    def get(self, receipt):
        bon = tc.teilstorno(receipt=receipt, amount=2000)
        cc.stopLoading(cc.getTransactionId(data[receipt]))
        self.render('bon.html', bon=bon)
        del data[receipt]


def make_app():

    return tornado.web.Application([
        (r"/", StartHandler),
        (r"/chooseChargePoint/", ChargePointHandler),
        (r"/showTarif/([^/]+)?", TarifHandler),
        (r"/authorise/([^/]+)?", AuthoriseHandler),
        (r"/abortAuth/", AbortHandler),
        (r"/charge/([^/]+)?", ChargeHandler),
        (r"/stopCharge/([^/]+)?", StopTransHandler),
        (r"/getAgb/", AgbHandler),
        (r"/getPP/", PPHandler)
    ],  debug=True,
        template_path=os.path.join(dirname, 'app', 'templates'),
        static_path=os.path.join(dirname, 'app')
    )


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    dirname = os.path.dirname(__file__)
    app = make_app()
    app.listen(8000)
    tc = TerminalController("192.168.178.89:22001")
    tornado.ioloop.IOLoop.current().start()
