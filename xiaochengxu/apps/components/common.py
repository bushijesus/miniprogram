from flask import jsonify

# 统一响应数据格式


def returnData(code, msg, data):
    returnjsondict = {
        "code": code,
        "msg": str(msg),
        "data": data
    }
    return jsonify(returnjsondict)
