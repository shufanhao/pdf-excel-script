import pdfplumber
import pandas as pd
# import logging

from pandas import DataFrame

# logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
import re

table_name_rex = "5.\d+ (.+)"
filed_name_rex = "5.\d+.\d+ (.+)"

end_flag_rex = "6 .+"

"""
要素名称  产品登记编码 \n英文名称  Product Pregition Code \n定义  理财产品的标识码 \n值域   \m数据表示  C14 \n备注  1.  系统自动生成。 
"""
field_column_regex = (
    r"(.|\n)*要素名称 +(?P<yaosuName>.+)\n英文名称 +(?P<englishName>(.|\n)*)\n定义 +(?P<define>(.|\n)*)\n值域 +(?P<zhiyu>(.|\n)*)\n数据表示 +(?P<dataDefine>(.|\n)*)\n备注 +(?P<beizhu>(.|\n)*)"
)


class PdfToExcel:
    # Pdf refer: https://www.cnblogs.com/sonictl/p/12247186.html
    # write to excel refer: https://zhuanlan.zhihu.com/p/363810440
    def __init__(self, file_path="example.pdf"):
        self.file_path = file_path
        self.tables = []
        self.tables_fields = []
        self.excel_datas = []  # [{"sheet_name": "example", "datas": [['zs', 'ls', 'ww'], ['man', 'man', 'woman']]}]

    def get_sheet_datas(self, sheet_name):
        for sheet in self.excel_datas:
            if sheet['sheet_name'] == sheet_name:
                return sheet['datas']

        sheet_data = {"sheet_name": f"{sheet_name}", "datas": []}
        self.excel_datas.append(sheet_data)
        return sheet_data["datas"]

    # def get_table_name_raw_field_by_field(self, field_without_number):
    #     """
    #     Get table name filed and raw_field, e.g: field_without_number: 产品名称, raw_field should be 5.1.1 产品名称
    #     :return: table name
    #     """
    #     for table_field in self.tables_fields:
    #         for field in table_field["fields"]:
    #             if field_without_number in field:
    #              return [table_field["table_name"], field]
    #
    #     raise Exception(f"cannot find table name by {field_without_number}")

    # def extract_tables(self, page_start, page_end=None):
    #     with pdfplumber.open(self.file_path) as pdf:
    #         for i in range(page_start - 1, page_end):
    #             page = pdf.pages[i]
    #             for field in page.extract_tables():
    #                 # 要素名称
    #                 yaosu_name = field[0][1]
    #                 # 英文名称
    #                 english_name = field[1][1]
    #                 # 定义
    #                 define = field[2][1]
    #                 # 值域
    #                 zhiyu = field[3][1]
    #                 # 数据表示
    #                 data_define = field[4][1]
    #                 # 备注
    #                 beizhu = field[5][1]
    #
    #                 table_name_raw_field = self.get_table_name_raw_field_by_field(yaosu_name)
    #                 sheet_datas = self.get_sheet_datas(table_name_raw_field[0])
    #                 # build line based on column
    #                 line = [5, '理财中心', '产品信息', '产品信息', '发行登记', yaosu_name, '', '', table_name_raw_field[1], define, zhiyu, data_define, beizhu]
    #                 logging.info(f"Appending sheet {table_name_raw_field[0]} with line: {line}" )
    #                 sheet_datas.append(line)
    #
    #         pdf.close()

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

    # def get_table_field(self, table_name):
    #     for table_filed in self.tables_fields:
    #         if table_filed["table_name"] == table_name:
    #             return table_filed
    #
    #     return {"table_name": None, "fields": []}

    # def parse_table_name_field_name(self, catalogue):
    #     table_name = None
    #     for line in catalogue.splitlines():
    #         table_m = re.match(table_name_rex, line)
    #         filed_m = re.match(filed_name_rex, line)
    #         if table_m:
    #             table_name = table_m.group(1)
    #             self.tables_fields.append({"table_name": table_name, "fields": []})
    #         elif filed_m:
    #             self.get_table_field(table_name)["fields"].append(filed_m.group(0))
    #         else:
    #             pass

    def parse_pdf_build_pd(self, raw_content):
        filed_content = ""
        filed_name = None
        sheet_datas = None
        for line in raw_content.split("\n"):
            table_m = re.match(table_name_rex, line)
            filed_m = re.match(filed_name_rex, line)
            end_m = re.match(end_flag_rex, line)
            if table_m:
                table_name = table_m.group(1)
                sheet_datas = self.get_sheet_datas(table_name)
                filed_content = self.generate_excel_line(filed_content, filed_name, sheet_datas)
            elif filed_m:
                print(f"Match filed: {filed_m.group(0)}")
                filed_content = self.generate_excel_line(filed_content, filed_name, sheet_datas)
                filed_name = filed_m.group(0)
            elif end_m:
                m = re.match(field_column_regex, filed_content)
                filed_content = self.generate_excel_line(filed_content, filed_name, sheet_datas)
                print(f"Finish parsing... end with line {line}")
            else:
                filed_content = filed_content + line + '\n'

    def generate_excel_line(self, filed_content, filed_name, sheet_datas):
        m = re.match(field_column_regex, filed_content)
        if m:
            excel_line = [5, '理财中心', '产品信息', '产品信息', '发行登记', m.group("yaosuName").rstrip(), '', '', filed_name.rstrip(), m.group("define").rstrip(), m.group("zhiyu").rstrip(),
                          m.group("dataDefine").rstrip(), m.group("beizhu").rstrip()]
            print(f"Generated excel line: {excel_line}")
            sheet_datas.append(excel_line)
            filed_content = ''
        return filed_content

    def write_into_excel(self):
        # colom name
        data = {'编号': [], '报送机构': [], '一级分类': [], '二级分类': [], '报表': [], '字段': [], '样例': [], '表结构备注': [], '报送文档来源ID': [], '定义': [], '值域': [], '数据表示': [], '备注': []}
        df = DataFrame(data)
        for sheet_datas in self.excel_datas:
            for i in range(len(sheet_datas["datas"])):
                df.loc[i] = sheet_datas["datas"][i]

        df.to_excel('output.xlsx', sheet_name="test", index=False, header=True)

    def main(self):
        # 读取目录：
        raw_content = self.extract_txt(2, 2)
        self.parse_pdf_build_pd(raw_content)
        self.write_into_excel()
        # catalogue = self.extract_txt(1, 1)
        # logging.info(f"catalogue: {catalogue}")
        # # parse 目录，提取table name and filed name
        # self.parse_table_name_field_name(catalogue)
        # # parse tables
        # self.extract_tables(2, 2)
        # # save to excel
        # self.write_into_excel()


if __name__ == '__main__':
    pdf = PdfToExcel()
    pdf.main()
    # print(pdf.extract_txt(1, 2))
    # pdf.extract_tables(2, 2)
    # pdf.write_into_excel()
    # pdf.main()
