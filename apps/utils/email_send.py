import random
from django.core.mail import EmailMessage
from django.template import loader  # 发送html格式的邮件

from Mxonline3.settings import EMAIL_FROM
from users.models import EmailVerifyRecord


# 生成随机字符串
def random_str(random_length=8):
    code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    for i in range(random_length):
        code += random.choice(chars)
    return code


# 发送邮件
def send_email(email, send_type='register'):
    # 生成随机的code放入链接
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)

    email_record = EmailVerifyRecord(
        code=code, email=email, send_type=send_type,
    )
    email_record.save()

    # 定义邮件内容:
    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = '微慕课 注册激活链接'
        # email_body = '欢迎注册mooc小站:  请点击下面的链接激活你的账号: http://127.0.0.1:8000/active/{0}'.format(code)

        email_body = loader.render_to_string('email_register.html', {'active_code': code})
        msg = EmailMessage(email_title, email_body, EMAIL_FROM, [email])
        msg.content_subtype = 'html'  # 邮件格式为HTML
        msg.send()  # 发送邮件

    elif send_type == 'forget':
        email_title = '微慕课 找回密码链接'
        email_body = loader.render_to_string('email_forget.html', {'active_code': code})
        msg = EmailMessage(email_title, email_body, EMAIL_FROM, [email])
        msg.content_subtype = 'html'
        msg.send()

    elif send_type == 'update_email':
        email_title = '微慕课 修改邮箱验证码'
        email_body = loader.render_to_string('email_update_email.html', {'active_code': code})
        msg = EmailMessage(email_title, email_body, EMAIL_FROM, [email])
        msg.content_subtype = 'html'
        msg.send()