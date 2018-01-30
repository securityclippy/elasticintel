from datetime import datetime
import socket
import re
import validators

def is_valid_ip(ipaddress):
    if valid_ipv4(ipaddress):
        return True
    if valid_ipv6(ipaddress):
        return True
    return False


def valid_ipv6(ipaddress):
    try:
        socket.inet_pton(socket.AF_INET6, ipaddress)
        return True
    except socket.error:
        return False


def valid_ipv4(ipaddress):
    try:
        socket.inet_pton(socket.AF_INET, ipaddress)
        return True
    except socket.error:
        return False


def is_md5(hash):
    regex = re.compile('^[a-f0-9]{32}')
    if re.match(regex, hash):
        return True
    return False


def is_sha1(hash):
    regex = re.compile('[a-fA-F0-9]{40}')
    if re.match(regex, hash):
        return True
    return False


def is_sha256(hash):
    regex = re.compile('[A-Fa-f0-9]{64}')
    if re.match(regex, hash):
        return True
    return False


def is_valid_port(port):
    if type(port) == int:
        if port <= 65535:
            return True
    return False

def is_proxy(proxy):
    #proxies should be in format of ipaddress:port or domain:port
    if proxy.split(":"):
        if is_valid_ip(proxy.split(":")[0]) or validators.domain(proxy.split(":")[0]):
            if int(proxy.split(":")[1]) > 0:
                if int(proxy.split(":")[1]) < 65535:
                    return True
    return False




