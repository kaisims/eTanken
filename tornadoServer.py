import os
import platform
import time
from abc import ABC

import tornado.ioloop
import tornado.web
import tornado.template
from tornado.web import RequestHandler

import asyncio
from app.terminalController import *
from app.chargeCloudController import *

data = dict(paid=False)

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
            chargepoint["url"] = "/authorise/" + chargepoint["id"]
            print(chargepoint['url'])
        self.render('chargepoints.html', chargepoints=chargepoints)


class AuthoriseHandler(RequestHandler):
    def get(self, evseid):
        if tc.checkConnection():
            if not data['paid']:
                self.render('authorisation.html', euro=12, url="/", evseid=evseid)
                tc.setupterminal()
                #receipt = 5
                receipt = tc.preAuthorisation()
                #TODO receipt zu cc schicken
                if receipt:
                    data['receipt'] = receipt
                    data['paid'] = True
                else:
                    data['paid'] = False
                print("Authorisation was %s" % data['paid'])
            else:
                link = '/charge/' + str(data['receipt'])
                self.redirect(url=link, permanent=False)
                print("Redirected %s" % link)
                cc.startLoading(evseid)
        else:
            self.write('Hmm kein Terminal zu finden')

    def options(self, evseid):
        if data['paid']:
            print("send isPayed")
            self.set_status(200)
            self.write(str(data['receipt']))
            self.finish()
        else:
            print("send isnotPayed")
            self.set_status(102)
            self.finish()


class ChargeHandler(RequestHandler):
    def get(self, receipt):
        self.render('charge.html', receipt=receipt)


class AgbHandler(RequestHandler):
    def get(self):
        cc.getAGB()
        self.write(cc.getAGB())


class PPHandler(RequestHandler):
    def get(self):
        self.write(cc.getPP())


class StopTransHandler(RequestHandler):
    def post(self, receipt):
        amount = self.get_argument('amount')
        tc.teilstorno(receipt=receipt, amount=amount)
        data["paid"] = False
        self.set_status(200)
        self.finish()

    def get(self, receipt):
        bon = tc.teilstorno(receipt=receipt, amount=2000)
        cc.stopLoading()
        data["paid"] = False
        self.render('bon.html', bon=bon)


def make_app():

    return tornado.web.Application([
        (r"/", StartHandler),
        (r"/chooseChargePoint/", ChargePointHandler),
        (r"/authorise/([^/]+)?", AuthoriseHandler),
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
