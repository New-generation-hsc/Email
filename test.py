from Email.pop import POP3
from datetime import datetime
import unittest


class TestPOP3(unittest.TestCase):

    def setUp(self):
        self.pop = POP3('pop.163.com')
        self.pop.connect()
        self.pop.login('hsc199761@163.com', 'huang199761hsc')

    def test_server(self):
        self.assertTrue(self.pop.server)

    def test_authenticate(self):
        self.assertEqual(self.pop.active, True)

    def test_mails(self):
        n = 10
        mails = self.pop.recent_mails(n=10)
        self.assertEqual(len(mails), n)

    def test_download(self):
        msg = self.pop.download(n=10)
        self.assertIn('From', msg[1])
        self.assertIn('Subject', msg[2])
        self.assertTrue(isinstance(msg[1]['Date'], datetime))

    def tearDown(self):
        self.pop.close()

if __name__ == '__main__':
    unittest.main()
