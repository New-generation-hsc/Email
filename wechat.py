from Email.pop import POP3
import itchat

client = POP3('pop.163.com')
client.connect()
client.login('hsc199761@163.com', '********')


def handle(message):
    msg_dict = None
    if u'周' in message:
        msg_dict = client.latest(week=True)
    elif u'月' in message:
        msg_dict = client.latest(month=True)
    elif u'最近' in message:
        msg_dict = client.latest()
    else:
        itchat.send('亲爱的主人，是不是手滑输错命令了？', toUserName='filehelper')
    if not msg_dict:
        for key in msg_dict:
            date = msg_dict[key]['Date']
            from_ = msg_dict[key]['From']
            subject = msg_dict[key]['Subject']
            msg1 = u'发件时间: {}\n'.format(date)
            msg2 = u'发件人: {}\n'.format(from_)
            msg3 = u'主题: {}\n\n'.format(subject)
            msg = msg1+msg2+msg3
            itchat.send(msg, toUserName='filehelper')
            print("么么哒，亲爱的小主人，正在发送第{}邮件信息".format(key+1))


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    content = msg['Content']
    print(content)
    if '163' in content or u'邮箱' in content:
        client.status = True
        itchat.send('我的主人，你现在可以接收邮件了，赶紧试试吧！！\n\n \
1、最近一份邮件\n \
2、最近一周的邮件\n \
3、本月的全部邮件\n 直接输中文哦！！', toUserName='filehelper')
    if u'关闭' in content:
        client.status = False
        itchat.send('我的主人，你关闭了接收邮件！！要不打卡看看。\n', toUserName='filehelper')
    if client.status:
        handle(message=content)


if __name__ == '__main__':
    itchat.auto_login(True)
    itchat.run()
