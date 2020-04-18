import asyncio
from ecrterm.ecr import ECR
from ecrterm.packets.types import ConfigByte


e = ECR(device='socket://192.168.178.89:22001', password='000000')


def checkConnection():
    # Kreditkarten Terminal anmelden
    try:
        connection = e.detect_pt()
    except Exception:
        connection = False
    return connection


async def main():
    #TODO Check if Ladepunkt ist bereit
    register()
    receipt = await preAuthorisation()
    #TODO Sende Ladevorgang starten an Backend
    #TODO Per Javascript? Display ändern
    #TODO Warte auf Antwort
    bon = await teilstorno(receipt=receipt, amount=2500)
    printer(bon)
    #TODO Upload Bon
    #TODO wieder auf Startseite

def register():
    e.register(config_byte=ConfigByte.ALL, tlv={0x26: {0x0A: b'\x06\xD1'}})
    e.wait_for_status()
    status = e.status()
    if status:
        print('Status code of PT is %s' % status)
        # laut doku sollte 0x9c bedeuten, ein tagesabschluss erfolgt
        # bis jetzt unklar ob er es von selbst ausführt.

        if status == 0x9c:
            print('End Of Day')
            e.end_of_day()
            # last_printout() would work too:
            printer(e.daylog)
        else:
            print('Unknown Status Code: %s' % status)
            # status == 0xDC for ReadCard (06 C0) -> Karte drin.
            # 0x9c karte draussen.


async def preAuthorisation(amount=5000):
    receipt = e.preauthorisation(amount_cent=amount)
    if receipt:
        e.wait_for_status()
        e.show_text(
            lines=['Zahlung autorisiert!'], beeps=1)
        return receipt
    else:
        e.wait_for_status()
        e.show_text(
            lines=['Ein Fehler ist aufgetreten'],
            beeps=2)
        return None


async def teilstorno(receipt=None, amount=10):
    if e.preauthorisationreverse(receipt=receipt, amount_cent=amount):
        bon = e.last_printout()
        e.wait_for_status()
        e.show_text(
            lines=['Auf Wiedersehen!', 'Zahlung erfolgt'], beeps=1)
        return bon
    else:
        e.wait_for_status()
        e.show_text(
            lines=['Ein Fehler ist aufgetreten'], beeps=2)
        return False


def printer(lines_of_text):
    for line in lines_of_text:
        print(line)
