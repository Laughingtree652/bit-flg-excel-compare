import json
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
import re


def process_info(string):
    bitflags = re.findall(r'bitFlg=\d+', string)
    return list(map(convert, bitflags))


def convert(bitflag):
    v = bitflag.replace("bitFlg=", "")
    return dec_str_to_bin_str(v)


def dec_str_to_bin_str(s):
    return str(bin(int(s))).replace("0b", "")


def compare_cmd_bit_flg(bit_a, bit_b):
    """

    :param bit_a: 待比较的第一个bitflg
    :param bit_b: 待比较的第二个bitflg
    :return: 第一个返回值表示待比较的bitflg是否一致，第二个返回值表示哪几个位数存在差异
    """
    ignore_list = [4, 16]
    diffs = []

    bit_a, bit_b = bit_a[::-1], bit_b[::-1]
    if len(bit_a) != len(bit_b):
        return False, []
    for i in range(0, len(bit_a)):
        if bit_a[i] != bit_b[i] and i not in ignore_list:
            diffs.append(i)
    return len(diffs) == 0, diffs


def main_process(input, output):
    """
    主要处理函数，将bitflg差异信息写出到新的列
    :param input: 输入的白盒对比结果差异文件.xlsx路径
    :param output: 输出结果路径
    :return:
    """
    # 临时设置显示全部行
    pd.set_option('display.max_rows', None)
    # 临时设置显示全部列
    pd.set_option('display.max_columns', None)

    df = pd.read_excel(input, sheet_name='cli_final')

    df['old_bitFlg'] = df['old_info'].apply(lambda x: process_info(x))
    df['new_bitFlg'] = df['new_info'].apply(lambda x: process_info(x))
    df['bitFlg_diff'] = None
    old_bitFlg_index = df.columns.get_loc('old_bitFlg')
    new_bitFlg_index = df.columns.get_loc('new_bitFlg')
    bitFlg_diff_index = df.columns.get_loc('bitFlg_diff')

    for index, row in df.iterrows():
        old_flgs = row.old_bitFlg
        new_flgs = row.new_bitFlg
        for i in range(0, len(old_flgs)):
            is_same, diffs = compare_cmd_bit_flg(old_flgs[i], new_flgs[i])
            # 存在差异时，将差异写入此列，字典的key表示第几个bitflg存在差异，value表示该bitflg的哪几位存在差异
            if not is_same:
                if df.iloc[index, bitFlg_diff_index] is None:
                    df.iloc[index, bitFlg_diff_index] = str({i: diffs})
                else:
                    new_val = json.loads(df.iloc[index, bitFlg_diff_index])
                    new_val[i] = diffs
                    df.iloc[index, bitFlg_diff_index] = str(new_val)

    print(df)
    # df.to_excel(output, index=False)


if __name__ == "__main__":
    input_path = r'..\whitebox-compare.xlsx'
    output_path = r'..\result-0920.xlsx'
    main_process(input_path, output_path)


