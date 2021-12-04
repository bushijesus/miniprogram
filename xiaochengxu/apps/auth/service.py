from flask_sqlalchemy import SQLAlchemy

from apps import db, app
from apps.sdk.wechat import WXSDK_jscode2session, WXSDK_userinfo

from apps.module import LoginSessionCache, Userdata


def login(request):
    '''获取前端传回来的code 并判断是否存在 如不存在则返回400'''
    code = request.json.get('code')
    if code == None:
        return 400, '参数不存在', ''

    else:
        try:
            '''获取用户的openid 和 session_key'''
            # 获取用户openid和session_key
            wechet_data = WXSDK_jscode2session(request.json['code'])
            openid, session_key = wechet_data['openid'], wechet_data['session_key']

            # 获取用户信息
            wechet_userdata = WXSDK_userinfo(openid, session_key)

            '''登录逻辑(更新和新建)'''
            if LoginSessionCache.query.filter_by(openid=openid).first():

                '''存在就更新session_key'''
                db.session.query(LoginSessionCache).filter(LoginSessionCache.openid == openid).update(
                    {LoginSessionCache.session_key: session_key})
                '''更新用户数据'''
                db.session.query(Userdata).filter(Userdata.openid == openid).update({
                    Userdata.username: wechet_userdata['nickName'],
                    Userdata.avatar: wechet_userdata['avatarUrl'],
                    Userdata.gender: wechet_userdata['gender'],
                    Userdata.country: wechet_userdata['country'],
                    Userdata.province: wechet_userdata['province'],
                    Userdata.city: wechet_userdata['city']
                })

                return 200, '成功', {"openid": openid, "session_key": session_key}

            else:
                '''不存在就创建登录记录写入id和sessionkey'''
                LoginSessionCache(openid, session_key)
                '''创建用户关联数据表'''
                Userdata(openid=openid,
                         username=wechet_userdata['nickName'],
                         avatar=wechet_userdata['avatarUrl'],
                         gender=wechet_userdata['gender'],
                         country=wechet_userdata['country'],
                         province=wechet_userdata['province'],
                         city=wechet_userdata['city'])

                return 200, '成功', {"openid": openid, "session_key": session_key}

        except:
            return 500, '内部错误', ''
