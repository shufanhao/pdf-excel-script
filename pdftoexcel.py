import pdfplumber
from pandas import DataFrame

import re

# 文档中是以5.x 打头 开始匹配table
table_name_rex = "5.\d+ (.+)"
field_name_rex = "5.\d+.\d+ (.+)"

# 根据6 xxx 匹配结束
end_flag_rex = "6 .+"

field_column_regex = (
    r"(.|\n)*要素名称 +(?P<yaosuName>.+)\n英文名称 +(?P<englishName>(.|\n)*)\n定义 +(?P<define>(.|\n)*)\n值域 +(?P<zhiyu>(.|\n)*)\n数据表示 +(?P<dataDefine>(.|\n)*)\n备注 +(?P<beizhu>(.|\n)*)"
)

column = {'表名': [], '编号': [], '报送机构': [], '一级分类': [], '二级分类': [], '报表': [], '字段': [], '样例': [], '表结构备注': [], '报送文档来源ID': [], '定义': [], '值域': [], '数据表示': [], '备注': []}


class PdfToExcel:
    # Pdf refer: https://www.cnblogs.com/sonictl/p/12247186.html
    # write to excel refer: https://zhuanlan.zhihu.com/p/363810440
    def __init__(self, file_path="example.pdf"):
        self.file_path = file_path
        self.tables = []
        self.tables_fields = []
        self.excel_datas = []  # [['zs', 'ls', 'ww'], ['man', 'man', 'woman']]

    def extract_txt(self, page_start, page_end):
        """
        extract txt
        :param page_start: index from 1
        :param page_end: index from 1
        :return:
        """
        with pdfplumber.open(self.file_path) as pdf:
            content = ''
            for i in range(page_start - 1, page_end):
                page = pdf.pages[i]
                # page.extract_text()函join数即读取文本内容，下面这步是去掉文档最下面的页码
                page_content = '\n'.join(page.extract_text().split('\n')[:-1])
                content = content + page_content
            pdf.close()
            return content

    def parse_pdf_build_pd(self, raw_content):
        """
        Parse pdf txt line by line based on regex to match different field, there is little tricky.
        :param raw_content:
        :return:
        """
        field_content = ""
        field_name = None
        table_name = None
        for line in raw_content.split("\n"):
            table_m = re.match(table_name_rex, line)
            field_m = re.match(field_name_rex, line)
            end_m = re.match(end_flag_rex, line)
            if table_m:
                print(f"Start processing table: {table_m.group(1).rstrip()}")
                if table_name is None:
                    table_name = table_m.group(1).rstrip()
                else:
                    field_content = self.generate_excel_line(field_content, field_name, table_name)
                    table_name = table_m.group(1).rstrip()

            elif field_m:
                print(f"Match field: {field_m.group(0)}")
                field_content = self.generate_excel_line(field_content, field_name, table_name)
                field_name = field_m.group(0)
            elif end_m:
                field_content = self.generate_excel_line(field_content, field_name, table_name)
                print(f"Finish parsing... end with line {line}")
            else:
                field_content = field_content + line + '\n'

    def generate_excel_line(self, field_content, field_name, table_name):
        """
        Generate one excel line if field_content matched by regex
        :return:
        """
        m = re.match(field_column_regex, field_content)
        if m:
            excel_line = [table_name, 5, '理财中心', '产品信息', '产品信息', '发行登记', m.group("yaosuName").rstrip(), '', '', field_name.rstrip(), m.group("define").rstrip(), m.group("zhiyu").rstrip(),
                          m.group("dataDefine").rstrip(), m.group("beizhu").rstrip()]
            print(f"Generated excel line: {excel_line}")
            self.excel_datas.append(excel_line)
            field_content = ''
        return field_content

    def write_into_excel(self):
        df = DataFrame(column)
        for i in range(len(self.excel_datas)):
            df.loc[i] = self.excel_datas[i]

        df.to_excel('output.xlsx', sheet_name="fanhaoawcl", index=False, header=True)
        print(f"Generated excel with sheet name: fanhaoawcl")

    def main(self):
        # 读取目录：
        raw_content = self.extract_txt(2, 3)
        self.parse_pdf_build_pd(raw_content)
        self.write_into_excel()


if __name__ == '__main__':
    pdf = PdfToExcel()
    pdf.main()
