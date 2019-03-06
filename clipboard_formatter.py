# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 18:54:46 2018

@author: Ivan
"""

from formatter import r_script_reformat, format_sql
import argparse
import pyperclip
parser = argparse.ArgumentParser()

parser.add_argument("-r", "--r", action="store_true",
                    help="Move to new DB")
args = parser.parse_args()
sql = pyperclip.paste()
out = format_sql(sql)
if args.r:
    out = r_script_reformat(sql)
else:
    out = format_sql(sql)

pyperclip.copy(out)