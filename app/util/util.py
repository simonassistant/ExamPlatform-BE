import hashlib
from datetime import datetime

def md5_encode(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

def to_bool(text: str, default: bool = False)-> bool:
    if text is None or text=='':
        return default
    text = text.strip().lower()
    if default:
        return not (text == 'false' or text == '0')
    else:
        return text == 'true' or text == '1'

def to_datetime(text: str)-> datetime:
    format_str:str = '%Y-%m-%d %H:%M:%S' if text.find('-') >= 0 else '%Y/%m/%d %H:%M:%S'
    return datetime.strptime(text, format_str)

def respond_suc(data: dict) -> dict:
    return {
        "code": 0,
        "msg": "success",
        "data": data
    }

def respond_fail(code: int = -1, msg: str='fail', data: dict = None) -> dict:
    return {
        "code": code,
        "msg": msg,
        "data": data
    }
