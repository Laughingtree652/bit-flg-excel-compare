import unittest
from src.main import compare_cmd_bit_flg, dec_str_to_bin_str


class MyTests(unittest.TestCase):
    def test_simple_compare(self):
        self.assertTrue(
            compare_cmd_bit_flg(dec_str_to_bin_str('10356736'),
                                dec_str_to_bin_str('10356752'))[0])


if __name__ == "__main__":
    unittest.main()