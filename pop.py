from email.utils import parsedate
from email.utils import parseaddr
from email.parser import Parser
from email.header import decode_header
from functools import wraps
from pprint import pprint
import time
import datetime
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
        self.status = False

    def connect(self):
        if self.server is None:
            try:
                self.server = poplib.POP3(self.pop3_server, self.port)
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
    def recent_mails(self):
        """download email from the server
        the default download number is 10"""
        resp, mails, octets = self.server.list()
        return mails

    @decorator
    def download(self, mails):
        """download the given mails from server"""
        msg_dict = dict()
        for index, mail in enumerate(mails):
            mail_index = mail.decode('utf-8').split()[0]   # A mail is like b'2 1953'
            resp, lines, octets = self.server.retr(mail_index)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            from_ = self._decode_address(msg['From'])
            subject = self._decode_str(msg['Subject'])
            date = self.parse_time(msg['Date'])
            msg_dict.setdefault(index, {})
            msg_dict[index]['From'] = from_
            msg_dict[index]['Subject'] = subject
            msg_dict[index]['Date'] = date
        return msg_dict

    def latest(self, week=False, month=False):
        if week and month:
            raise AttributeError("Week and Month can't be True simultaneous")
        mails = self.recent_mails()
        start = int(mails[0].decode('utf-8').split()[0])  # mail is like b'1 1586'
        end = int(mails[len(mails) - 1].decode('utf-8').split()[0])
        if week:
            n = self._latest_email(mails, start, end, 7)
            latest_mail = self.download(mails[n-1:])
        elif month:
            days = datetime.datetime.now().day - 1
            n = self._latest_email(mails, start, end, days=days)
            latest_mail = self.download(mails[n-1:])
        else:
            latest_mail = self.download(mails[-1:])
        print(":)----------->一共采集了{} 封邮件".format(len(latest_mail)))
        return latest_mail

    def _latest_email(self, mails, start, end, days=1):
        """Return the given latest days email
        use binary search algorithm to find"""
        if start >= end:
            return start+1
        mid = (start + end) // 2
        resp, lines, octets = self.server.retr(mid)
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        tm = self.parse_time(msg['Date'])  # this is the email send time
        delay_time = datetime.datetime.now() - datetime.timedelta(days=days)
        if tm == delay_time:
            return mid
        elif tm > delay_time:
            return self._latest_email(mails, start, mid-1, days)
        else:
            return self._latest_email(mails, mid+1, end, days)

    @staticmethod
    def parse_time(email_time):
        """Convert the email time to datetime"""
        struct_time = parsedate(email_time)
        time_stamp = time.mktime(struct_time)
        tm = datetime.datetime.fromtimestamp(time_stamp)
        return tm

    @classmethod
    def _decode_address(cls, addr):
        """convert the address to human readable"""
        head, address = parseaddr(addr)
        name = cls._decode_str(head)
        value = u'%s <%s>' % (name, address)
        return value

    @staticmethod
    def _decode_str(s):
        """convert the `subject`, `from` and `to` to human readable"""
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def close(self):
        """Close the connection with the server"""
        if self.server is not None:
            self.server.quit()


class POPConnectionError(Exception):
    """if pop3 client don't connect with the server,
    then it will raise this error"""
    pass


class POPAuthenticateError(Exception):
    """An Authentication Error exception
    if user must login in to do some operation"""
    pass


if __name__ == '__main__':
    client = POP3('pop.163.com')
    client.connect()
    client.login('******', '******')
    pprint(client.latest(month=True))
    client.close()
