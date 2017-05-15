from email.utils import parsedate
from email.utils import parseaddr
from email.parser import Parser
from email.header import decode_header
from functools import wraps
import poplib


def decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.server is None:
            raise POPConnectionError("Connect with the pop3 server first.")
        if not self.active:
            raise POPAuthenticateError("Authentication Error, login in first.")
        return func(self, *args, **kwargs)
    return wrapper


class POP3(object):
    """A Mail User Agent
    As Client to receive to email from server
    `pop server`: pop.sina.com
    port: 110 default
    active: judge the user is online or login in.
    """
    def __init__(self, pop3_server, port=110):
        self.pop3_server = pop3_server  # pop3 server like pop.163.com
        self.port = port  # port like 163 ---> 496
        self.server = None
        self.active = False

    def connect(self):
        if self.server is None:
            try:
                self.server = poplib.POP3_SSL(self.pop3_server, self.port)
            except BaseException as e:
                print(":) oh, no. the error is %s" % e)
                self.server = None

    def login(self, username, password):
        if self.server is None:
            raise POPConnectionError("Connect with the pop3 server first.")
        try:
            self.server.user(username)
            self.server.pass_(password)
            self.active = True
        except poplib.error_proto:
            print("Authentication failed. please check your email and your password.")

    @decorator
    def recent_mails(self, n=10):
        """download email from the server
        the default download number is 10"""
        resp, mails, octets = self.server.list()
        return mails[-n:]

    def download(self, n=10):
        mails = self.recent_mails(n)
        msg_dict = dict()
        for mail in mails:
            mail_index = mail.decode('utf-8').split()[0]   # A mail is like b'2 1953'
            resp, lines, octets = self.server.retr(mail_index)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            from_ = msg['From']

class POPConnectionError(Exception):
    """if pop3 client don't connect with the server,
    then it will raise this error"""
    pass


class POPAuthenticateError(Exception):
    """An Authentication Error exception
    if user must login in to do some operation"""
    pass
