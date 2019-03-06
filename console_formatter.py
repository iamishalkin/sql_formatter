# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 17:31:57 2018

@author: Ivan
"""
from formatter import r_script_reformat, format_sql
from functions import move_to_new_database
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("fpath", type=str,
                    help="Path to R script")
parser.add_argument("-ndb", "--new_db", action="store_true",
                    help="Move to new DB")
parser.add_argument("-sql", "--sql", action="store_true",
                    help="Format only sql")
args = parser.parse_args()
with open(args.fpath, "r+") as f:
     rscript = f.read() # read everything in the file
     f.seek(0) # rewind
     if args.sql:
         out = format_sql(rscript)
     else:
         out = r_script_reformat(rscript, insert_linebreak = False)
     if args.new_db:
         out = move_to_new_database(out)
     f.write(out) # write the new line before

