# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.


class Utils:

    @staticmethod
    def baFromStringToBytearray(sString):
        uiLength = len(sString)
        if uiLength%2 != 0 or uiLength == 0 :
            return None
        if not Utils.bChkHexString(sString, uiLength):
            return None
        baRet=bytearray()
        for uiI in range(0, uiLength//2):
            baRet.append(int(sString[uiI*2:uiI*2+2], 16) )
        return baRet

    @staticmethod
    def sFromBytearrayToString(baByteArray):
        if type(baByteArray) is bytes or type(baByteArray) is bytearray:
            return ''.join('{:02X}'.format(a) for a in baByteArray)
        else:
            return ""

    @staticmethod
    def bChkHexString(sData, uiLength):
        if len(sData) != uiLength:
            return False
        for uiI in range (0, len(sData) ):
            try:
                int(sData[uiI], 16)
            except Exception as e:
                return False
        return True

    @staticmethod
    def baFromStringToAsciiBytearray(sString):
        baRet=bytearray()
        for my_char in sString:
            baRet.append(ord(my_char))
        return baRet

    @staticmethod
    def sFromAsciiBytearrayToString(baAsciiData):
        sRet=""
        for my_byte in baAsciiData:
            sRet = sRet + chr(my_byte)
        return sRet

    @staticmethod
    def Hex(uiInteger):
        return '{:X}'.format(abs(uiInteger))

    @staticmethod
    def Hex2(ucByte):
        return '{:02X}'.format(abs(ucByte) & 0xff)

    @staticmethod
    def get_qry_dict(db_qry):
        """
        :param db_qry:
        :return:
        PROPÒSIT:
        Donada una query, n'obté el dicionari i n'elimina la clau '_sa_instance_state' que el sqlalchemy hi afegeix.
        """
        itemdb_dict = dict(db_qry.__dict__)
        if '_sa_instance_state' in itemdb_dict.keys():
            del itemdb_dict['_sa_instance_state']
        return itemdb_dict