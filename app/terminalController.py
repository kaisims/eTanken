import asyncio
from ecrterm.ecr import ECR
from ecrterm.packets.types import ConfigByte


class TerminalController(ECR):

    def __init__(self, ip=None):
        self.ip = ip
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

    def preauthorisation(self, amount=1500, listener=None):
        receipt = ECR.preauthorisation(self, amount_cent=amount)
        if receipt:
            self.wait_for_status()
            return receipt
        else:
            self.wait_for_status()
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


def printer(lines_of_text):
    for line in lines_of_text:
        print(line)
