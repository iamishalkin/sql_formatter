#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Mishalkin Ivan
"""
 
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QShortcut, QFileDialog, QDesktopWidget, QTextEdit, QPushButton, QHBoxLayout, QSplitter,  QApplication)
from PyQt5.QtCore import Qt, QCoreApplication, QRegExp
from PyQt5.QtGui import QFont, QKeySequence, QSyntaxHighlighter, QTextCharFormat
from formatter import format_sql, r_script_reformat
from functions import to_clipboard, move_to_new_database


class Format(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):      
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        self.font_size = 10#default font
        self.center()
        """Left and right editors with Courier font and horizontal scroll"""
        self.topleft = QTextEdit(self)
        self.topleft.setFont(QFont("Courier", self.font_size))
        self.topleft.setLineWrapColumnOrWidth(2500)
        self.topleft.setLineWrapMode(QTextEdit.FixedPixelWidth)
  
        self.topright = QTextEdit(self)
        self.topright.setFont(QFont("Courier", self.font_size))
        self.topright.setLineWrapColumnOrWidth(2500)
        self.topright.setLineWrapMode(QTextEdit.FixedPixelWidth)
        #buttons
        button = QPushButton("Beautify!")
        button.clicked.connect(self.beautify)
        button.setShortcut('Ctrl+B')
        button.setToolTip('Ctrl+B')
        copy_button = QPushButton("Copy to clipboard")
        copy_button.clicked.connect(self.to_clipboard)
        copy_button.setShortcut('Ctrl+Shift+C')
        copy_button.setToolTip('Ctrl+Shift+C')
        open_button = QPushButton("Open R")
        open_button.clicked.connect(self.showDialog)
        open_button.setShortcut('Ctrl+O')
        open_button.setToolTip('Ctrl+O')
        save_button = QPushButton("Save R")
        save_button.clicked.connect(self.file_save)
        save_button.setShortcut('Ctrl+S')
        save_button.setToolTip('Ctrl+S')
        beautifile_button = QPushButton("BeautiFILE!")
        beautifile_button.clicked.connect(self.beautifile)
        beautifile_button.setShortcut('Ctrl+Shift+B')
        beautifile_button.setToolTip('Ctrl+Shift+B')
        highlight_cb = QCheckBox('Highlight', self)
        highlight_cb.stateChanged.connect(self.highlight)
        new_db_button = QPushButton('Move to new DB')
        new_db_button.clicked.connect(self.move_to_new_db)
        new_db_button.setShortcut('Ctrl+N')
        new_db_button.setToolTip('Ctrl+N')
        #set relative position of buttons
        vbox.addWidget(button)
        vbox.addWidget(copy_button)
        vbox.addWidget(open_button)
        vbox.addWidget(save_button)
        vbox.addWidget(beautifile_button)
        vbox.addWidget(highlight_cb)
        vbox.addWidget(new_db_button)
        vbox.addStretch(1)
        #hotkeys to change font size
        font_plus = QShortcut(QKeySequence("Ctrl++"), self)
        font_plus2 = QShortcut(QKeySequence("Ctrl+="), self)
        font_plus.activated.connect(self.font_plus)
        font_plus2.activated.connect(self.font_plus)
        font_minus = QShortcut(QKeySequence("Ctrl+-"), self)
        font_minus.activated.connect(self.font_minus)
        #splitter to make editors resizable 
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.topleft)
        splitter1.addWidget(self.topright)
        hbox.addWidget(splitter1)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('SQL Formatter')
        self.show()
        
    def beautify(self):
        #format SQL
        sql = self.topleft.toPlainText()
        out = format_sql(sql)
        self.topright.clear()
        self.topright.insertPlainText(out)
        
    def to_clipboard(self):
        to_clipboard(self.topright.toPlainText())

    def center(self):
        #move window to centre of the screen
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())        
        
    def showDialog(self):
        #open R script
        fname = QFileDialog.getOpenFileName(self, 'Open File', '', 'Rscripts (*.r *.R)',
               None, QFileDialog.DontUseNativeDialog)
        print(fname)
        f = open(fname[0], 'r')
        with f:        
            data = f.read()
            self.topleft.setText(data)
            r_out = r_script_reformat(data)
            self.topright.clear()
            self.topright.setText(r_out)
            
    def file_save(self):
        #save text from left editor window
        name = QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name,'w')
        text = self.topright.toPlainText()
        file.write(text)
        file.close()
            
    def beautifile(self):
        #format SQLs from r script, pasted to left editor
        r_script = self.topleft.toPlainText()
        r_out = r_script_reformat(r_script, insert_linebreak = False)
        self.topright.clear()
        self.topright.insertPlainText(r_out)
        
    def font_plus(self):
        #enlarge fontsize
        self.font_size +=1
        self.topleft.setFont(QFont("Courier", self.font_size))
        self.topright.setFont(QFont("Courier", self.font_size))
        
    def font_minus(self):
        #reduce fontsize
        self.font_size -=1
        self.topleft.setFont(QFont("Courier", self.font_size))
        self.topright.setFont(QFont("Courier", self.font_size))        
    
    def move_to_new_db(self):
        #apply multi_replace to change DB tablenames and alias
        old = self.topright.toPlainText()
        new = move_to_new_database(old)
        self.topright.setText(new)
        
    def highlight(self, state):
        #highlight alias and tablenames from new DB
        if state == Qt.Checked:
            self.highlighter = Highlighter(self.topright.document())
        else:
            self.highlighter.setDocument(None)
        

#https://github.com/baoboa/pyqt5/blob/master/examples/richtext/syntaxhighlighter.py
class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)
        

        #Keywords should be added here and in functions move_to_new_database
        self.keywordPatterns = ['prime',  'corporate_actions_research',
                                'equity_dividend',  'equity_dividend_adj_factor',
                                'equity_fundamentals',  'equity_security_content',
                                'equity_security_master',  'equity_split_or_spin_events',
                                'gic_fx_rate',  'giw_index_summary',  'giw_index_weight',
                                'reuters_fx_rate',  'saxtat',  'security_mapping',
                                'tso_research',  'esc',  'esm',  'evaluation_date',
                                'index_composure_date']

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in self.keywordPatterns]

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        
if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = Format()
    sys.exit(app.exec_())