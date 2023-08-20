import crcmod.predefined


class Crc:
    __Crc8 = crcmod.mkCrcFun(poly=0x131, initCrc=0xff, xorOut=0x00, rev=True)
    __Crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xffff, xorOut=0x0000, rev=True)

    def caculateCrc8(dataPackage):
        return Crc.__Crc8(dataPackage)

    def caculateCrc16(dataPackage):
        return Crc.__Crc16(dataPackage)

    def verifyCrc8(dataPackage):
        return Crc.__Crc8(dataPackage[:-1]) == dataPackage[-1]

    def verifyCrc16(dataPackage):
        return Crc.__Crc16(dataPackage[:-2]) == int.from_bytes(dataPackage[-2:], "little")

