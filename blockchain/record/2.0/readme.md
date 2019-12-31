运行环境：Python 3.7  
所需包：requests、Flask  
\
\
\
web页面地址(可以进行添加链、查看链、查看其它节点操作)  
`http://192.168.0.1:5000`
\
\
\
获取链信息  
`curl -X GET "http://192.168.0.1:5000/chain"`
\
\
\
获取其它节点信息  
`curl -X GET "http://192.168.0.1:5000/nodes"`
\
\
\
新增一条记录  
```
curl -X POST "http://192.168.0.1:5000/record/new" -H "Content-Type: application/json" -d'
{
  "name": "张三",
  "type": "远程支持",
  "scope": "数据库",
  "detail": "解决数据库启动异常问题",
  "region": "宁波",
  "tag": "MySQL",
  "time": "2019-12-12",
  "duration": "1H",
  "product": "测试项目",
  "department": "软件研发中心-研发一部",
  "contact": "李四"
}
'
```
\
\
注册一个新的节点  
```
curl -X POST "http://192.168.0.1:5000/nodes/register" -H "Content-Type: application/json" -d'
{
  "nodes": ["http://192.168.0.2:5000"]
}
'
```
\
\
对该节点的权威性进行校验  
`curl -X GET "http://192.168.0.1:5000/nodes/resolve"`

