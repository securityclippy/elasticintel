import ipaddress


class IOCValidator(object):
    def __init__(self):
        blerp = "berp"

    @staticmethod
    def  is_valid_ipaddress(ip_string):
        try:
            ipaddress.ip_address(ip_string)
        except Exception as e:
            return False
        return True

    @staticmethod
    def is_valid_url(url_string):
        if "http" in url_string:
            return True
        return False
