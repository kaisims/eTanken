import os
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
        if tc.checkConnection():
            #TODO cc check if Ladepunkt bereit
            self.render('start.html', url="authorise/")
        else:
            self.write('Hmm kein Terminal zu finden')


class AuthoriseHandler(RequestHandler):

    def get(self):
        if tc.checkConnection():
            if not data['paid']:
                self.render('authorisation.html', euro=12, url="/")
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
                link = 'charge/' + str(data['receipt'])
                self.redirect(url=link, permanent=False)
                print("Redirected %s" % link)
        else:
            self.write('Hmm kein Terminal zu finden')

    def options(self):
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
        #TODO cc check if Ladepunkt bereit
        self.render('charge.html', receipt=receipt)


class StopTransHandler(RequestHandler):
    def post(self, transactionid):
        self.set_status(200)
        self.finish()


def make_app():

    return tornado.web.Application([
        (r"/", StartHandler),
        (r"/authorise/", AuthoriseHandler),
        (r"/charge/([^/]+)?", ChargeHandler),
        (r"/stopCharge/([^/]+)?", StopTransHandler)
    ],  debug=True,
        template_path=os.path.join(dirname, 'app', 'templates'),
        static_path=os.path.join(dirname, 'app')
    )


if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    app = make_app()
    app.listen(8000)
    tc = TerminalController("192.168.178.89:22001")
    tornado.ioloop.IOLoop.current().start()
