# -*- coding: utf-8 -*-

# pip install pycryptodome

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from urllib.parse import quote_plus
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """

    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    @staticmethod
    def ordered_data(data):
        complex_keys = []
        for k, val in data.items():
            if isinstance(val, dict):
                complex_keys.append(k)

        # 将字典类型的数据dump出来
        for k in complex_keys:
            data[k] = json.dumps(data[k], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        p_key = self.app_private_key
        signer = PKCS1_v1_5.new(p_key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        p_key = self.alipay_public_key
        signer = PKCS1_v1_5.new(p_key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)

# if __name__ == "__main__":
# 测试代码
# from urllib.parse import urlparse, parse_qs
# alipay = AliPay(
#     appid="2016102600761595",
#     app_notify_url="http://81.70.37.90:8081/alipay/return",
#     app_private_key_path="/home/lichy/project/MxShop/apps/trade/keys/private_2048.txt",
#     alipay_public_key_path="/home/lichy/project/MxShop/apps/trade/keys/alipay_2048_key.txt",
#     # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
#     debug=True,  # 默认False,
#     return_url="http://81.70.37.90:8081/alipay/return"
# )
#
# return_url = 'http://81.70.37.90/?charset=utf-8&out_trade_no=20170202122666688&method=alipay.trade.page.pay.return&total_amount=100.00&sign=dQ6hIyDBYQLLb%2FkfqSLJMGSKhlwqYFFpQw4GRUq8hbwDoPUTdL49Kbr%2FJ1xzCIf11IAgye4JgLGkihgLaEEM3lkTp0gep2a3%2B7xsivkrY7I59E15x1XNmwIw97HG2zZpiG9Gzb5zTiCSwb3h5usU9ZRRUr9mpDU6XuLNsYteJr0G%2BclHqiZPCih8PGl4ahu33uLJ%2F8IMNjRwklGpfdAaAj6%2Fh1cYZVgNSrHFibL0VHRSwVoff4gI2ARj9lcwUHMS1SRJKl5olTFUp3NMPc5OjnYVuIdnI1Y6jQ8vwBeNhU9rFt3T9ptl5uEQ1Sv5SwGBbW8c8TiSOQQPcOBux4vfqQ%3D%3D&trade_no=2020072022001402290500991953&auth_app_id=2016102600761595&version=1.0&app_id=2016102600761595&sign_type=RSA2&seller_id=2088102181084902&timestamp=2020-07-20+10%3A07%3A25'
# o = urlparse(return_url)
# query = parse_qs(o.query)
# processed_query = {}
# ali_sign = query.pop("sign")[0]
# for key, value in query.items():
#     processed_query[key] = value[0]
# print(alipay.verify(processed_query, ali_sign))
#
# url = alipay.direct_pay(
#     subject="测试订单",
#     out_trade_no="20170202122666622k",
#     total_amount=100,
#     return_url="http://81.70.37.90/alipay/return"
# )
# re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
# print(re_url)
