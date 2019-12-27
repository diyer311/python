挖矿  
`curl -X GET "http://192.168.0.1:5000/mine"`  


获取链信息  
`curl -X GET "http://192.168.0.1:5000/chain"`

新增一个交易  
```
curl -X POST "http://192.168.0.1:5000/transactions/new" -H "Content-Type: application/json" -d'
{
  "sender": "abcdefg",
  "recipient": "1234567",
  "amount": 5
}
'
```

注册一个新的节点  
```
curl -X POST "http://192.168.0.1:5000/nodes/register" -H "Content-Type: application/json" -d'
{
  "nodes": ["http://192.168.0.1:5001"]
}
'
```

对该节点的权威性进行校验  
`curl -X GET "http://192.168.0.1:5000/nodes/resolve"`



参考博文链接如下：  
https://learnblockchain.cn/2017/10/27/build_blockchain_by_python
