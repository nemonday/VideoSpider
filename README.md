
`第一 安装go，配置好GOPATH环境变量`
     
     GOPATH由自己定义 export GOPATH=xxxxx
     最好把工程入到GOPATH/src
     
     工程目录在：
        GOPATH/src/ym


`第二 安装rocketmq client cpp，支持rocketMQ消息`
 
    从https://github.com/apache/rocketmq-client-cpp.git
    
    根据网站 https://github.com/apache/rocketmq-client-cpp描述，自行编译
    
    注：如果没有bzip2-dev 需要 apt-get install libbz2-dev
    
    运行 ./build.sh
    
    copy the library to /usr/local/lib
    
      cp ./bin/librocketmq.so /usr/local/lib
      cp ./bin/librocketmq.a  /usr/local/lib
      
    copy the head files to /usr/local/include/rocketmq
    
      cp ./include/*.*  /usr/local/include/rocketmq/
    

`第三 下载一些库，因为GOOGLE完全被WALL,所以需要从github下载后，再解压到GOPATH`
    
    在音盟的ym/ym-go/import.sh 描述了需要哪些库 
    
    可以直接从仓库：ym/ym-go-vendor/ 下载 vendor.zip包，解压GOPATH/src
    目录结构：
       
       src/github.com
       src/golang.com
       src/...

`第四 准备好protoc运行环境`
   
    从 https://github.com/protocolbuffers/protobuf 下载
    ./configure
    make
    make install
    
    linux 建议安装到: /usr/local目录下，执行configure时，指定--prefix=/usr/local/protobuf
    
    成功安装后，加入环境变量
    
    export PATH=$PATH:/usr/local/protobuf/bin
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/protobuf/lib
    
 `第五 安装grpc，这样可以用到grpc框架`
    go get -u github.com/golang/protobuf/protoc-gen-go
    
    cd $GOPATH/src/github.com/golang/protobuf/protoc-gen-go
    
    go build
    
    go install
    
    加入环境变量
    export PATH=$PATH:$GOPATH/bin