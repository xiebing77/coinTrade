from common.email_obj import EmailObj
from jinja2 import Environment, FileSystemLoader
from setup import *


def reserve_float(value, float_digits=0):
    value_str = str(value)
    value_list = value_str.split('.')
    if len(value_list) == 2:
        new_value_str = '.'.join([value_list[0], value_list[1][0:float_digits]])
    else:
        new_value_str = value_list[0]
    return float(new_value_str)


def send_report(orders, accounts, to_addr, subject='Coin Trade Daily Report', cc_addr=''):
    # construct html
    env = Environment(
        loader=FileSystemLoader(template_dir),
    )
    template = env.get_template('template.html')
    html = template.render(orders=orders, accounts=accounts)
    # print(html)
    email_obj = EmailObj(email_srv, email_user, email_pwd)
    email_obj.send_mail(subject, html, email_user, to_addr, cc_addr)
