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
    ignore_list = [4, 16]
    diffs = []

    bit_a, bit_b = bit_a[::-1], bit_b[::-1]
    if len(bit_a) != len(bit_b):
        return False, []
    for i in range(0, len(bit_a)):
        if bit_a[i] != bit_b[i] and i not in ignore_list:
            diffs.append(i)
    return len(diffs) == 0, diffs


if __name__ == "__main__":
    # 临时设置显示全部行
    pd.set_option('display.max_rows', None)
    # 临时设置显示全部列
    pd.set_option('display.max_columns', None)

    df = pd.read_excel(r'..\whitebox-compare.xlsx')

    rows, columns = df.shape
    row_labels = df.index
    column_labels = df.columns
    print(row_labels, column_labels)

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
            if not is_same:
                if df.iloc[index, bitFlg_diff_index] is None:
                    df.iloc[index, bitFlg_diff_index] = str({i: diffs})
                else:
                    new_val = json.loads(df.iloc[index, bitFlg_diff_index])
                    new_val[i] = diffs
                    df.iloc[index, bitFlg_diff_index] = str(new_val)

    print(df)
    df.to_excel(r'..\result-0920.xlsx', index=False)


