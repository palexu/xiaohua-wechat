from flask import Flask
from flask import request
import time
import hashlib
from flask_script import Manager
import xml.etree.ElementTree as ET

import dispacher

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def valid():
    echostr = request.args.get('echostr')
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    
    api = wechatCallbackApi()
    if(api.check_signature(signature,timestamp,nonce)):
        return echostr
    else:
        return None

@app.route('/',methods=['post'])
def response():
    postStream = request.stream.read()
    api = wechatCallbackApi()
    toUser,fromUser,userContent = api.get_request_text(postStream)
    responseText = dispacher.dispacher(userContent)
    return api.create_response_xml_text(fromUser,toUser,responseText)



class wechatCallbackApi:
    def check_signature(self,signature, timestamp, nonce):
        token = "palexu"
        L = [timestamp, nonce, token]
        L.sort()
        s = L[0] + L[1] + L[2]
        return hashlib.sha1(s.encode('utf-8')).hexdigest() == signature

    def get_request_text(self,PostXML):
        """Get the content of user query"""
        PostXML = ET.fromstring(PostXML)
        ToUser = PostXML.find("ToUserName").text
        FromUser = PostXML.find("FromUserName").text
        UserContent  = PostXML.find("Content").text

        return ToUser,FromUser,UserContent

    def create_response_xml_text(self,toUser,fromUser,RespContent):
        """ format the response text content and response"""
        RespFomat = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        RespXML = RespFomat % (toUser,fromUser,int(time.time()),RespContent)
        return RespXML


if __name__ == '__main__':
    manager.run()