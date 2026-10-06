# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import re


class KCheck:

    @staticmethod
    def floatInInterval(iInputValue, Min, Max):
        floatvalue = float(iInputValue)
        if floatvalue >= Min and floatvalue <= Max:
            return floatvalue
        else:
            raise Exception('K_FloatInInterval_CheckError')

    @staticmethod
    def integerInInterval(iInputValue, Min, Max):
        integervalue = int(iInputValue)
        if integervalue >= Min and integervalue <= Max:
            return integervalue
        else:
            raise Exception('K_IntegerInInterval_CheckError')

    @staticmethod
    def integerInList(iInputValue, ListOfValues):
        integervalue = int(iInputValue)
        if integervalue in ListOfValues:
            return integervalue
        else:
            raise Exception('K_IntegerInList_CheckError')

    @staticmethod
    def elementInList(element, ListOfElements):
        if element in ListOfElements:
            return element
        else:
            raise Exception('K_elementInList_CheckError')

    @staticmethod
    def booleanValue(bInputValue):
        if type(bInputValue) == bool:
            return bInputValue
        elif type(bInputValue) == int:
            return bool(bInputValue)
        elif type(bInputValue) == str:
            if bInputValue.lower() == 'true':
                return True
            elif bInputValue.lower() == 'false':
                return False
            else:
                raise Exception('K_BooleanValue_CheckError')
        else:
            raise Exception('K_BooleanValue_CheckError')

    @staticmethod
    def bytearrayLenInInterval(baInputValue, LenMin, LenMax):
        if type(baInputValue) == str:
            bavalue = bytearray.fromhex(baInputValue)
        else:
            bavalue = bytearray(baInputValue)
        if len(bavalue) >= LenMin and len(bavalue) <= LenMax:
            return bavalue
        else:
            raise Exception('K_BytearrayLenInInterval_CheckError')

    @staticmethod
    def hexStringLenInInterval(sData, LenMin, LenMax):
        if type(sData) != str:
            raise Exception('K_hexStringLenInInterval_CheckError')
        if len(sData) < LenMin or len(sData) > LenMax:
            raise Exception('K_hexStringLenInInterval_CheckError')
        for uiI in range(0, len(sData)):
            int(sData[uiI], 16)
        return sData

    @staticmethod
    def decStringLenInInterval(sData, LenMin, LenMax):
        if type(sData) != str:
            raise Exception('K_decStringLenInInterval_CheckError')
        if len(sData) < LenMin or len(sData) > LenMax:
            raise Exception('K_decStringLenInInterval_CheckError')
        for uiI in range(0, len(sData)):
            int(sData[uiI])
        return sData

    @staticmethod
    def stringLenInInterval(sData, LenMin, LenMax):
        if type(sData) != str:
            raise Exception('K_stringLenInInterval_CheckError')
        if len(sData) < LenMin or len(sData) > LenMax:
            raise Exception('K_stringLenInInterval_CheckError')
        return sData

    @staticmethod
    def is_printable(input_string):
        """
       Validate if the input_string contains printable characters only.

       Args:
           input_string (str): String.

       Returns:
           bool: True if the format is valid, False otherwise.
       """
        pattern = r'^[\x20-\x7E]+$'
        return bool(re.match(pattern, input_string))

    @staticmethod
    def validate_url(url_string):
        """
        Validate the format of a string containing a URL.

        Args:
            url_string (str): String containing a URL.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        url_pattern = re.compile(
            r"(?:(?:http|https)://)?"  # scheme (optional)
            r"(?:\S+(?::\S*)?@)?"  # credentials
            r"(?:(?P<host>[^:/?#\s]+)(?::(?P<port>\d+))?)?"  # host and port
            r"(?P<path>/[\w/_.-]*)?"  # path
            r"(?:\?(?P<query>[\w=&]+))?"  # query string
            r"(?:#(?P<fragment>\S+))?$"  # fragment
        )
        return bool(url_pattern.match(url_string))

    @staticmethod
    def validate_email(email_string):
        """
        Validate the format of a string containing an email address.

        Args:
            email_string (str): String containing an email address.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        return bool(email_pattern.match(email_string))

    @staticmethod
    def validate_charset_for_password(password):
        """
        •	Lowercase letters: a to z
        •	Uppercase letters: A to Z
        •	Digits: 0 to 9
        •	Special characters: '!', '#', '$', '%', '&', '(', ')', '*', '-', '.', '/', '<', '=', '>', '?', '@', '^', '_', '¡', '¿'
        """
        # En el pattern el backslash s'usa per escapar el guió mig i el punt. Caracters especials ordenats per ascii
        pattern = r'^[a-zA-Z0-9!#$%&()*\-\./<=>?@^_¡¿]+$'
        return re.match(pattern, password) is not None

    @staticmethod
    def is_complex_password(input_string):
        """
        Validate if the input_string contains a complex password. Entenent:
            * Minimum length of 8 characters.
            * At least one uppercase letter.
            * At least one lowercase letter.
            * At least one digit (0-9).
            * At least one special character among !, #, $, %, &, (, ), *, -, /, =, ?, @, ^, _, ¡, ¿

        Args:
           input_string (str): String.

        Returns:
           bool: True if the format is valid, False otherwise.
        """
        # En el pattern el backslash és per escapar el guió mig. Caracters especials ordenats per ascii
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!#$%&()*\-/=?@^_¡¿&])[A-Za-z\d@$!#$%&()*\-/=?@^_¡¿&]{8,}$'
        return bool(re.search(pattern, input_string))

    @staticmethod
    def is_valid_mac_address(mac_address):
        # Define the regular expression pattern for MAC address
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac_address))

    @staticmethod
    def is_ending_in_list(input_string, endings_list):
        for ending in endings_list:
            if input_string.endswith(ending):
                return True
        return False