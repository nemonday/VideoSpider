
`基于手机app， 微信小程序，视频平台的视频爬取及数据入库`
     
     所需环境
     使用框架:scrapy
     使用工具包: selenium, mts
     ps:
        mts安装：
        mts用于视频上传存储等功能
        # 官方文档说明
        如果能使用外网访问，请使用pip 进行安装
        – 执行命令install aliyun-python-sdk-mts 进行安装
        – 修改$PYTHON_HOME/lib/site-packages/aliyunsdkcore/endpoint.xml文件，找到Mts标签 项，填入实际的DomainName地址
        – 升级。执行pip install aliyun-python-sdk-mts –upgrade完成升级
        – 卸载。执行pip uninstall aliyun-python-sdk-mts完成卸载 通过源码安装，该方式主要用于无法访问外网的情况下进行访问
        – 解压aliyun_python_sdk_mts-2.x.zip包
        – 进入解压目录
        – 执行python setup.py install即可。
        
        
        - 一般只需 sudo pip install aliyun-python-sdk-mts 即可
       
     其余所需要的模块：在env.text自行搜寻找安装

`框架使用`
 
    爬虫使用及所需条件，所有爬虫在VideoSpider/spiders当中
    本地使用方法：只需在 VideoSpider/start.py 文件中把 cmdline.execute("scrapy crawl {输入想要启动爬虫的名字}".split()) 右键运行即可
    爬虫状况：
        hk（好看视频app）：
            可以使用，直接运行即可
        ky （开眼视频app）：
            因为视频质量问题已停止维护，数据可以提取出来，存在bug：视频下载，关于请求头，代理之类有一些校验，会导致无法下载视频 （此爬虫需求运行一次即可爬取其全站的信息）
        ppx （皮皮虾app）：
            因为视频都是竖屏不符合要求已经停止维护， 数据可以提取出来， 下载去水印等操作，没有写
        pq（票圈长视频）：
            可以直接使用
        td （糖豆广场舞小程序）
            可以直接使用 （运行一次即可爬取全站， 此站视频时长都很长，去水印时间很长，很消耗性能，同时视频用户反馈一般）
        uc  （ucapp）
            可以直接使用 （此爬虫只做数据爬取入库， 视频下载需要配合VideoSpider/Tool/xg_video使用，xg_video 使用selenium获取下载地址进行视频下载，同时修改数据库信息）
        xg  （西瓜视频）
            因为视频水印太多，停止维护
        xng （小年糕小程序）
            可以直接使用 （但是代码中 item['token'] = '8f8135b40677be896a6270ddff99cb71'
                                    item['uid'] = '9077df59-0135-4ecf-abaa-eae77159673b' 是会过期的，需要在小程序上刷新视频的时候抓包更新）
        xngzf （小年糕祝福）
            与小年糕小程序同理
            
    爬虫使用注意事项：
        因为此爬虫跟线上逻辑有出入，此爬虫只是把筛选出来的视频下载到本地，上传oss功能已经被注释
        爬虫有水印模糊功能：环境不一样需要自己配置路径，需要在VideoSpider/API/iduoliaotool.py dewatermark模块中修改ffmpeg工具的路径，环境配有软链，可以直接写成ffmpeg
        由于此爬虫不是最终版本，只是给运营应急使用，写了很多本地的下载路径， 此路径需要自行修改
        
    

`部署`
    
    使用的爬虫管理部署，基于scrapyd， spiderkeeper 生成的ui爬虫管理工具
    部署参考：https://blog.csdn.net/mouday/article/details/80408795