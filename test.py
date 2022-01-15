import re
str = "'5 数据源目录 要素名称  产品登记编码% \n英文名称  Product Pregition Code \n定义  理财产品的标识码 \n值域   \n数据表示  C14 \n备注  1.  系统自动生成。"

str = "5 数据元目录 \n要素名称  产品名称 \n英文名称  Product Name \n定义  发行机构赋予理财产品的称谓。试试很迷茫世纪东方是咖啡机肯德基福克\n斯九分裤上岛咖啡快递费快递费交付数据发快递是副科级 \n值域   \n数据表示  c.. 200 \n备注  1.  必填 \n2.  需要填写产品实际对外销售的全称 \n3.  产品名字不能含有任何符号 \n \n \n'"

str = "要素名称  产品登记编码 \n英文名称  Product Pregition Code \n定义  理财产品的标识码 \n值域   \n数据表示  C14 \n备注  1.  系统自动生成。 \n \n \n"
field_column_regex = (
    # r"(?P<fullLine>要素名称 +(?P<yaosuName>[\u4e00-\u9fa5]+) +\n英文名称 +(?P<englishName>.+) +\n.+"
    r"(.|\n)*要素名称 +(?P<yaosuName>.+)\n英文名称 +(?P<englishName>(.|\n)*)\n定义 +(?P<define>(.|\n)*)\n值域 +(?P<zhiyu>(.|\n)*)\n数据表示 +(?P<dataDefine>(.|\n)*)\n备注 +(?P<beizhu>(.|\n)*)"
)

m = re.match(field_column_regex, str)      # 不在起始位置匹配
print(m.group("yaosuName"))
print(m.group("englishName"))
print(m.group("define"))
print(m.group("zhiyu"))
print(m.group("dataDefine"))
print(m.group("beizhu").rstrip())