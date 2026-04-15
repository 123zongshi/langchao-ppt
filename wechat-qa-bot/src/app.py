# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import time
import os
import hashlib
import xml.etree.ElementTree as ET

app = Flask(__name__)

WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'shangqiu2026')

def verify_signature(token, timestamp, nonce, signature):
    tmp_list = sorted([token, timestamp, nonce])
    tmp_str = ''.join(tmp_list)
    hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
    return hash_obj.hexdigest() == signature

def parse_xml_message(xml_str):
    try:
        root = ET.fromstring(xml_str)
        msg_dict = {}
        for child in root:
            text = child.text.strip() if child.text else ''
            msg_dict[child.tag] = text
        return msg_dict
    except:
        return None

def search_product(keyword):
    # 简单版本：直接返回查询内容
    return f"收到查询：{keyword}\n\n报表功能稍后开启，当前可查询以下产品：\n- 星bookPro14 (fs0021)\n- 星book16\n- 战66\n\n如需查询其他产品，请联系管理员更新报表。"

@app.route('/', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        if echostr:
            return echostr
        if signature and timestamp and nonce:
            if verify_signature(WECHAT_TOKEN, timestamp, nonce, signature):
                return echostr or 'ok'
        return 'WeChat Bot is running!'
    else:
        xml_data = request.data.decode('utf-8')
        msg_dict = parse_xml_message(xml_data)
        if not msg_dict:
            return '', 200
        from_user = msg_dict.get('FromUserName', '')
        to_user = msg_dict.get('ToUserName', '')
        content = msg_dict.get('Content', '').strip()
        reply = search_product(content) if content else "请输入产品名称查询"
        xml = f"<xml><ToUserName><![CDATA[{from_user}]]></ToUserName><FromUserName><![CDATA[{to_user}]]></FromUserName><CreateTime>{int(time.time())}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{reply}]]></Content></xml>"
        return Response(xml, mimetype='application/xml')

application = app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 9000, app)
