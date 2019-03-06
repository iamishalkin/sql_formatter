# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 16:35:37 2018

@author: Ivan
"""
import re
import pyperclip

def fix_on(on_line, join_line):
    """This function splits line with 'ON' to two parts :
    before 'ON' and after with apropriate indention from 'JOIN' line"""
    on_part = re.sub(r'.* ON ', ' ON ', on_line)
    new_line = on_line[:-len(on_part)]
    indent = len(join_line) - len(join_line.lstrip())
    on_part = ' ' * indent + on_part.lstrip()
    return new_line, on_part
    
def fix_between(line):
    """This function separates line with 'BETWEEN' and 'AND'
    It returns line without 'AND' part and 'AND' part with appropriate indention"""
    trunc_between = line[line.index("BETWEEN"):]#re.search(r"BETWEEN.*", line).string
    and_date = re.sub(r'.*AND', 'AND', trunc_between)
    new_line = line[:-len(and_date)]
    indent = len(line[:line.index("BETWEEN")]) + 4
    and_date = ' ' * indent + and_date
    return new_line, and_date

def find_on_joins(splited):
    """This function matches index of 'JOIN' line with 'ON' line"""
    istart = []  # stack of indices of opening parentheses
    d = {}
    
    for i, c in enumerate(splited):
        if 'JOIN' in c:
            istart.append(i)
        if bool(re.search(' ON ', c)):
            try:
                d[istart.pop()] = i
            except IndexError:
                print('Too many closing ONs')
    
    dictlist = []
    
    for key, value in d.items():
        temp = [key,value]
        dictlist.append(temp)
    return list(dictlist)

def to_clipboard(text):
    """copy to clipboard"""
    pyperclip.copy(text)
    
def multi_replace(string, substitutions):
    """The function gets dict with replace patterns and return string with replaces"""
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

def move_to_new_database(sql):
    """Uses multi_replace to move from old DB to new"""
    substitutions = {'nasdaq_fundamentaldb_poc': 'prime',
                     'nasdaq_corp_actions_research': 'corporate_actions_research',
                     'nasdaq_dividend': 'equity_dividend',
                     'nasdaq_dividend_adj_factor': 'equity_dividend_adj_factor',
                     'nasdaq_pit_fundamentals': 'equity_fundamentals',
                     'nasdaq_security_content': 'equity_security_content',
                     'nasdaq_security_master': 'equity_security_master',
                     'nasdaq_split_or_spin_events': 'equity_split_or_spin_events',
                     'nasdaq_gic_fx_rates': 'gic_fx_rate',
                     'nasdaq_giw_index_summary': 'giw_index_summary',
                     'nasdaq_giw_index_weight': 'giw_index_weight',
                     'nasdaq_reuters_fx_rates': 'reuters_fx_rate',
                     'nasdaq_saxtat': 'saxtat',
                     'nasdaq_security_mapping': 'security_mapping',
                     'nasdaq_tso_research': 'tso_research',
                     'nsc': 'esc',
                     'nsm': 'esm',
                     'sec_content_date': 'evaluation_date',
                     'giw_trade_date': 'index_composure_date'}
    sql = multi_replace(sql, substitutions)
    return sql