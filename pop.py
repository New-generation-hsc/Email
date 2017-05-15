from email.utils import parsedate
from email.utils import parseaddr
from email.parser import Parser
from email.header import decode_header
import poplib


class POP3(object):
    """A Mail User Agent
    As Client to receive to email from server
    `pop server`: pop.sina.com
    port: 110 default
    """
    def __init__(self, pop3_server, port=110):
        
