#coding=utf-8
"""
usage:
python spider.py mv 西瓜

source: ~/code/python/scrap/Movie
"""
from bs4 import BeautifulSoup
import requests
import urllib.parse
import re
import sys
# from selenium import webdriver
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
    datefmt='%y-%m-%d %H:%M:%S',
    filename='spider.log',
    filemode='w'
    )

class Spider:
    def __init__(self):
        self.url='http://so.loldytt.com/search.asp'
        self.session=requests.Session()
        self.status=''
        self.valid()
    
    def valid(self):
        try:
            #尝试通过wangan参数来通过验证
            redir_url=self.get_url_with_wangan(self.url+'?keyword=hello')
            wangan=redir_url.split('&__wangan=')[1]
            logging.debug('wangan:'+wangan)
            html=self.session.get(self.url+'?keyword=hello&__wangan='+wangan)
            return '?__wangan='+wangan
        except Exception as e:
            logging.info(e)
            logging.info('该异常出现的原因：可能是之前建立的链接未中断')
            return ''

    def get_url_with_wangan(self,url):
        html=self.session.get(url)
        # 获取网安参数
        pre_content_has_url=html.text
        pattern_wangan=re.compile(r'"\S+?"')
        match_wangan=pattern_wangan.findall(pre_content_has_url)
        redir_url=''
        for i in match_wangan:
            redir_url+=i
        redir_url=redir_url.replace('"','')
        if '__wangan' not in redir_url:
            return ''
        print('==============================get_url_with_wangan:'+'http://www.loldytt.com'+redir_url)
        return 'http://www.loldytt.com'+redir_url

    def search(self,movie):

        html=self.session.post(self.url,params={'keyword':Transfer.toGb2312(movie)})

        bsobj=BeautifulSoup(html.text, "html.parser")
        htmlContent=Transfer.toUtf8(html.text)
        movieCount=self.__getNumOfMovie(htmlContent)
        if movieCount==None:
            logging.error("获取电影失败，可能是目标网站无响应")
            return None
        if movieCount==0:
            self.status='没有找到相关资源，可能资源较新暂未收录，或者你输入的电影名有误'    
        else:
            self.status='为你找到了%d部电影～回复序号获得迅雷链接\n'%movieCount
        
        n=movieCount//20
        m=movieCount%20
        if m>0:
            n=n+1

        urllist=[]
        for i in range(1,n+1):
            param={'keyword':Transfer.toGb2312(movie),'page':i}
            html=self.session.post(self.url,params=param)
            bsobj=BeautifulSoup(html.text, "html.parser")
            htmlContent=Transfer.toUtf8(html.text)
            urllist.append(self.__matchUrl(htmlContent))
        logging.debug("movie info collected")

        rs=[]
        for i in urllist:
            for j in i:
                rs.append(j)
        return rs

    def __matchMagnet(self,text):
        pattern=re.compile(r'thunder:\/\/[A-Za-z0-9\+\/=]*')
        match=pattern.findall(text)
        if match:
            return match[0]
        else:
            return ''

    def getMagnet(self,url):
        # html=self.session.get(url)
        # print("html:%s"%(Transfer.toUtf8(html.text)))
        s=self.get_url_with_wangan(url)
        try:
            html=self.session.get(s)
        except Exception as e:
            logging.warning(e)
            logging.warning('可能无须验证，那就直接访问吧')
            html=self.session.get(url)
        
        # print("html:%s"%(Transfer.toUtf8(html.text)))
        bsobj=BeautifulSoup(Transfer.toUtf8(html.text), "html.parser")
        lst=[]
        for i in bsobj.find_all('a',{'target':'_self'}):
            rs=self.__matchMagnet(str(i))
            if rs!='':
                tmp={'name':i.get_text(),'thunderLink':rs}
                logging.debug("magnet:%s"%(tmp))
                lst.append(tmp)
        return lst

    def __matchUrl(self,html):
        pattern=re.compile(r'http://www\.loldytt\.com/.*/.*/">.+</a>')
        urlPattern=re.compile(r'http://www\.loldytt\.com/[\w|\d]+/[\w|\d]+/')
        match=pattern.findall(html)

        lst=[]
        for i in match:
            tmpstr=i.replace('</a>','')
            try:
                url=urlPattern.match(tmpstr).group()
                mvName=tmpstr.replace(url+'">','')
                lst.append({'name':mvName,'url':url})
            except Exception as e:
                logging.warning("无法解析:%s"%tmpstr)
        return lst

    def __getNumOfMovie(self,html):
        pattern=re.compile(r'共找到<b>\d+</b>部')
        match=pattern.findall(html)
        if match:
            num=match[0].replace('共找到<b>','').replace('</b>部','')
            return int(num)

    def found(self,movie,inputList):
        for i in inputList:
            if movie==i['name']:
                return i['url']
        return False


class Movie:
    
    def getMovie(self,movie):
        spider=Spider()
        logging.info("spider running...")
        rs=spider.search(movie)
        if rs==None:
            return '未找到相关电影:\n可能是因为尚未收录该电影，或连接不到资源服务器\n'
        content=spider.status
        for index,item in enumerate(rs):
            logging.debug('%d|%s|%s'%(index,item['name'],item['url']))
            content+='%d|%s|%s\n'%(index,item['name'],item['url'])
        return content

    def getBtlink(self,url):
        spider=Spider()
        rs=spider.getMagnet(url)
        # for item in rs:
        #     print(item['thunderLink'])
        #     return
        return rs[0]['thunderLink']


class test:
    def printMovieInfo(self):
        print("""美国恐怖故事第二季EP01  thunder://QUFmdHA6Ly90djp0dkB4bGguMnR1LmNjOjMxNDU2L8PAufq/1rLAucrKwrXatv68vi9b0bjA18/C1Nh3d3cuMnR1LmNjXcPAufq/1rLAucrKwi612rb+vL5FUDAxLnJtdmJaWg==\n
美国恐怖故事第二季EP02  thunder://QUFmdHA6Ly9kczpkc0B4bGMuMnR1LmNjOjIxMjkyL8PAufq/1rLAucrKwrXatv68vi9b0bjA18/C1Nh3d3cuMnR1LmNjXcPAufq/1rLAucrKwi612rb+vL5FUDAyLnJtdmJaWg==\n
美国恐怖故事第二季EP03  thunder://QUFmdHA6Ly9kczpkc0B4bGMuMnR1LmNjOjIxMjk2L8PAufq/1rLAucrKwrXatv68vi9b0bjA18/C1Nh3d3cuMnR1LmNjXcPAufq/1rLAucrKwi612rb+vL5FUDAzLnJtdmJaWg==\n
美国恐怖故事第二季EP04  thunder://QUFmdHA6Ly9kczpkc0B4bGMuMnR1LmNjOjMxMjE3L8PAufq/1rLAucrKwrXatv68vi9b0bjA18/C1Nh3d3cuMnR1LmNjXcPAufq/1rLAucrKwi612rb+vL5FUDA0LnJtdmJaWg==\n
""")

    def test_matchMagnet(self):
        sp=Spider()
        tt='<a href="thunder://QUFmdHA6Ly9keTpkeUB4bGEueHVuYm8uY2M6MTAzNjgvW9G4wNfPwtTYd3d3Llh1bkJvLkNjXbCiuMrV/bSrQkQxMDI0uN/H5dbQ06LLq9fWLnJtdmJaWg==" title="阿甘正传BD1024高清中英双字" target="_self">阿甘正传BD1024高清中英双字</a>'
        print(spider.matchMagnet(tt))

    def test_isUrlCode(self):
        testString='E6%B5%8B%E你8%AF%95'
        print(isUrlCode(testString))


class Transfer:
    def toGb2312(text):
        try:
            return text.encode('gb2312')
        except Exception as e:
            logging.warning(e)
            return ""
        

    def toUtf8(text):
        try:
            return text.encode('ISO-8859-1').decode('gb2312')
            # return text.encode('ISO-8859-1').decode('utf-8')
            # return text.encode('ISO-8859-1').decode('utf-8')
        except Exception as e:
            logging.warning(e)
            return text
        

def isUrlCode(code):
    #有问题
    match=re.match(r'^[%\w]+$',code)
    if match:
        return True
    else:
        return False

if __name__ == '__main__':
    # click()
    if len(sys.argv)==2:
        #电影名
        movie=sys.argv[1]
        if movie=='test':
            te=test()
            te.printMovieInfo()
            # te.test_isUrlCode()
        else:
            # movie=urllib.parse.unquote(movie)
            logging.info("start search, movie:%s"%(movie))
            movieHandler=Movie()
            print(movieHandler.getMovie(movie))
            logging.info("finish search...")
    elif len(sys.argv)==3:
        #url bt
        url=sys.argv[1]
        cmd=sys.argv[2]
        logging.info("start get btlink: targetUrl->%s  cmd->%s"%(url,cmd))
        movieHandler=Movie()
        print(movieHandler.getBtlink(url))


    
