import asyncio
from ecrterm.ecr import ECR
from ecrterm.packets.types import ConfigByte


class TerminalController(ECR):

    def __init__(self, ip=None):
        self.ip=ip
        try:
            super().__init__(device='socket://'+ip+"?ssl=true", password='111111')
        except:
            self = None

    def checkConnection(self):
        # Kreditkarten Terminal anmelden
        try:
            connection = self.detect_pt()
        except:
            connection = False
        return connection

    def setupterminal(self):
        if self.transmitter is None:
            super().__init__(device='socket://'+self.ip+"?ssl=true", password='111111')
        self.register(config_byte=ConfigByte.ALL, tlv={0x26: {0x0A: b'\x06\xD1'}})
        self.wait_for_status()
        status = self.status()
        if status:
            print('Status code of PT is %s' % status)
            # laut doku sollte 0x9c bedeuten, ein tagesabschluss erfolgt
            # bis jetzt unklar ob er es von selbst ausführt.

            if status == 0x9c:
                print('End Of Day')
                self.end_of_day()
                # last_printout() would work too:
                printer(self.daylog)
            else:
                print('Unknown Status Code: %s' % status)
                # status == 0xDC for ReadCard (06 C0) -> Karte drin.
                # 0x9c karte draussen.

    def preauthorisation(self, amount=5000, listener=None):
        receipt = ECR.preauthorisation(self, amount_cent=amount)
        if receipt:
            self.wait_for_status()
            #self.show_text(lines=['Zahlung autorisiert!'], beeps=1)
            return receipt
        else:
            self.wait_for_status()
            self.show_text(
                lines=['Ein Fehler ist aufgetreten'],
                beeps=2)
            return None

    def teilstorno(self, receipt=0, amount=10):
        if self.partialcancellation(receipt=receipt, amount_cent=amount):
            bon = self.last_printout()
            self.wait_for_status()
            self.show_text(
                lines=['Auf Wiedersehen!', 'Zahlung erfolgt'], beeps=1)
            return bon
        else:
            self.wait_for_status()
            self.show_text(
                lines=['Ein Fehler ist aufgetreten'], beeps=2)
            return False

    def abort(self):
        ECR.abort(self)


def printer(lines_of_text):
    for line in lines_of_text:
        print(line)
