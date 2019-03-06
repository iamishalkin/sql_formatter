# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 19:49:27 2018

@author: Ivan
"""

import re
import sqlparse
import itertools
from functions import fix_on, fix_between, multi_replace, find_on_joins

def r_script_reformat(rscript, insert_linebreak = True):
    """Finds SQL betwen 'fetch_' and pipe(%>%) and produces format SQL to each match, then replaces old SQL with new"""
    list_of_sql_queries = re.findall('fetch_(.+?) %>%', rscript, re.S)
    
    substitutions = {'data("': '\n', 'data(': '', 'query = ': '', 'query= ': '', 'query=': '',
                    'query =': '', 'dglue("\n': '', 'dglue("': '', 
                    '")': '', '"))': ''}
    sqls = []
    for sql_query in list_of_sql_queries:
        sqls.append(multi_replace(sql_query, substitutions))
    
    formatted_sqls = []
    for idx, sql in enumerate(sqls):
        if insert_linebreak:
            formatted_sqls.append('\n' + format_sql(sql, linebreak_in_the_end = False))
        else:
            formatted_sqls.append(format_sql(sql, linebreak_in_the_end = False))
        #formatted_sqls[idx] = re.sub(r"\nSELECT", r"SELECT", formatted_sqls[idx])
        rscript = rscript.replace(sql.rstrip().rstrip("\n"), formatted_sqls[idx])
    rscript = rscript.rstrip()
    return rscript

def format_sql(sql, keywords_exceptions = ["source", "index"], linebreak_in_the_end = False):
    """Performs some additional editing to sql-parse editor"""
    sql = re.sub(r"from\(", r"FROM (", sql, flags=re.I)
    sql = re.sub(r" NULL ", r" NULLASDFG", sql) #to avoid redundant formatting in select part
    preformatted = sqlparse.format(sql, reindent = True, keyword_case='upper')
    """Replace uppercased keywords to lowercase analog"""

    if keywords_exceptions:
        for kword in keywords_exceptions:
            preformatted = re.sub(r"\b" + kword.upper() + r"\b", kword.lower(), preformatted)
    
    splited = preformatted.splitlines()
    if "" in splited: splited.remove("")
    """ON BLOCK"""
    """Make same indention for related ONs and JOINs"""
    on_join_pairs = find_on_joins(splited)
    on_join_pairs = sorted(on_join_pairs,key=lambda x:(-x[1]))
    
    for joins, ons in on_join_pairs:
        new_on_line, on_part_line = fix_on(splited[ons], splited[joins])
        splited[ons] = new_on_line
        splited.insert(ons+1, on_part_line)
    
    final = "\n".join(splited)
    """WHEN THEN BLOCK"""
    splited = final.splitlines()
    
    lines_with_when = [i for i, word in enumerate(splited) if re.search("WHEN", word)]
    lines_with_when.sort(reverse = True)
    
    for idx, line in enumerate(lines_with_when):
        indent = len(splited[line])-len(splited[line].lstrip())
        it = list(itertools.takewhile(lambda x: "THEN" not in x, splited[line:]))
        line_with_then = len(it)
        then_line, then = splited[line + line_with_then].split('THEN')
        splited[line + line_with_then] = then_line.rstrip()
        splited.insert(line + line_with_then + 1, ' '*indent + 'THEN' + then.rstrip())

    final = "\n".join(splited)
    """AND after ON BLOCK"""
    """Makes additional indention for extra on-join criteria"""
    splited = final.splitlines()
    
    lines_with_and = [i for i, word in enumerate(splited) if re.search("(^|\W)ON ", word, re.IGNORECASE)]
    lines_with_and.sort(reverse = True) #get indices of lines with ON and arrange in descending order
    
    for idx, line in enumerate(lines_with_and):
        #Get indices of lines starting with 'AND' after 'ON'line
        it = list(itertools.takewhile(lambda x: x.lstrip()[:3] == "AND", splited[line+1:]))
        for next_string in range(len(it)):
            indent = len(splited[line])-len(splited[line].lstrip())+2
            splited[line+1+next_string] = " "*indent + splited[line+1+next_string]
            
    final = "\n".join(splited)
    """BETWEEN BLOCK"""
    """Dates in BETWEEN condition one after another"""
    splited = final.splitlines()
    lines_with_between = [i for i, word in enumerate(splited) if re.search('between', word, re.IGNORECASE)]
    lines_with_between.sort(reverse = True) 
    
    for idx in lines_with_between:
        between_line, and_line = fix_between(splited[idx])
        splited[idx] = between_line #initial line without and part
        splited.insert(idx+1, and_line) #insert and part under truncated between part
    
    final = "\n".join(splited)
    """PARTITION BLOCK"""
    splited = final.splitlines()
    lines_with_partition = [i for i, word in enumerate(splited) if re.search('PARTITION', word, re.IGNORECASE)]
    lines_with_lead = [i for i, word in enumerate(splited) if re.search("LEAD", word)]
    #Partition after lead, should not be changed
    lines_with_partition = [x for x in lines_with_partition if x not in lines_with_lead]
    lines_with_partition.sort(reverse = True)
    
    for idx, line in enumerate(lines_with_partition):
        if "," not in splited[line]:
            continue #nothing to do with one column
        part_cols = splited[line].split(",")
        if "" in part_cols: part_cols.remove("")
        last = part_cols[0].split()[-1] #take first column for indent calculation
        indent = len(part_cols[0]) - len(last)
        for index, column in enumerate(part_cols[1:]): #each new column on new line
            column = " " * indent + column.lstrip() + ","
            splited.insert(line+1+index, column)
    final = "\n".join(splited)
    """Indent after LEAD"""
    splited = final.splitlines()
    lines_with_lead = [i for i, word in enumerate(splited) if re.search("LEAD", word)]
    lines_with_lead.sort(reverse = True)
    
    try:
        for idx, line in enumerate(lines_with_lead):
            #Get indices of lines starting with 'AND' after 'ON'line
            it = list(itertools.takewhile(lambda x: len(x) - len(x.lstrip()) > 80, splited[line+1:]))
            for next_string in range(len(it)):
                if "PARTITION" in splited[line+next_string]:
                    indent = len(splited[line+next_string].split('PARTITION')[0])
                    splited[line+1+next_string] = " "*indent + splited[line+1+next_string].lstrip()
                    continue #some magic to handle partition after LEAD
                splited[line+1+next_string] = " "*indent + splited[line+1+next_string].lstrip()
    except:
        pass
    final = "\n".join(splited)
        
    """SUBSTRING BLOCK"""
    splited = final.splitlines()
    #find indices of lines with word SUBSTRING
    lines_with_substring = [i for i, word in enumerate(splited) if re.search('SUBSTRING', word, re.IGNORECASE)]
    lines_with_substring.sort(reverse = True)
    
    for line in lines_with_substring:
        substring_split = splited[line].split('SUBSTRING')
        indent = len(substring_split[0])
        splited[line] = substring_split[0] + 'SUBSTRING' + substring_split[1]
        for part in range(len(substring_split)-2):
            splited.insert(line+1+part, ' ' * indent + 'SUBSTRING' + substring_split[2+part])
    final = "\n".join(splited)
    """IN BLOCK"""
    splited = final.splitlines()
    
    lines_with_in = [i for i, word in enumerate(splited) if re.search(' IN ', word, re.IGNORECASE)]
    lines_with_in.sort(reverse = True) 
    
    
    for idx, line in enumerate(lines_with_in):
        #count the number of lines after in and before the closing parenthesis
        initial_line = splited[line]
        splited[line] = splited[line].split(' IN ')[1]
        amount_of_values = [i for i, word in enumerate(splited[line:]) if re.search(r'\)', word)][0]
        splited[line] = initial_line
        for following_lines in  range(amount_of_values):
            splited[line] = splited[line] + " " + splited[line + 1].lstrip()
            del splited[line + 1]
    
    
    splited = [s.rstrip() for s in splited]
    if not linebreak_in_the_end:
        pass
    final = "\n".join(splited)
    #finaly replace with NULL edited in the beginning column
    final = re.sub(r" NULLASDFG", r" NULL ", final)
    final = re.sub(r"\( ", r"(", final)
    final = re.sub(r" \)", r")", final)
    return final