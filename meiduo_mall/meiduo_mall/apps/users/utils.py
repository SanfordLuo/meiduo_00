import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义jwt认证成功返回数据"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """根据用户输入的账号查询user"""
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 手机号登陆
            user = User.objects.get(mobile=account)
        else:
            # 用户名登陆
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    """自定义登录验证后端，实现账号和手机号都登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 使用账号查询user对象
        user = get_user_by_account(username)

        # 如果user存在，使用user校验密码，如果密码校验通过，响应user
        if user and user.check_password(password):
            return user
