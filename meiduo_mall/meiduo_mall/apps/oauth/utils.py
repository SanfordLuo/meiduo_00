from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
import json
import logging

from .exceptions import QQAPIException



from . import constants

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        """
        获取qq登录的网址
        :return: url网址
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """获取access_token"""

        # 准备url
        url = 'https://graph.qq.com/oauth2.0/token?'
        # 准备参数
        params = {
            'grant_type':'authorization_code',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'code':code,
            'redirect_uri':self.redirect_uri
        }
        # 凭借地址
        url += urlencode(params)

        try:
            # 使用code向QQ服务器发送请求获取access_token
            response = urlopen(url)
            # 获取响应的二进制
            response_data = response.read()
            # 将response_data转成字符串
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
            response_str = response_data.decode()
            # 将response_str转成字典
            response_dict = parse_qs(response_str)
            # 提取access_token
            #  response_dict.get('access_token') == [FE04************************CCE2]
            access_token = response_dict.get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token失败')

        return access_token

    def get_openid(self, access_token):
        """
        使用access_token向QQ服务器请求openid
        :param access_token: 上一步获取的access_token
        :return: open_id
        """

        # 准备url
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        # 美多向QQ服务器发送请求获取openid
        response_str = ''
        try:
            response = urlopen(url)
            response_str = response.read().decode()

            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            response_dict = json.loads(response_str[10:-4])
            # 获取openid
            openid = response_dict.get('openid')
        except Exception as e:
            # 如果有异常，QQ服务器返回 "code=xxx&msg=xxx"
            data = parse_qs(response_str)
            logger.error(e)
            raise QQAPIException('code=%s msg=%s' % (data.get('code'), data.get('msg')))

        return openid

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_save_user_token(token):
        """
        检验保存用户数据的token
        :param token: token
        :return: openid or None
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('openid')
