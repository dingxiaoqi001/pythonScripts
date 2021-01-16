# hi


### 把json数据写入文件中会出现 中文无法显示的问题,所有中文显示为unicode编码,解决方法:
#### 加入ensure_ascii参数
```python
json.dumps({"text": "我可去年买了个表"},ensure_ascii=False))
```
