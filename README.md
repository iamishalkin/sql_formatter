# SQL_Formatter

## Description

Tool for nice SQL formatting, based on [sql-parse](https://github.com/andialbrecht/sqlparse) with additional features. Console and UI versions.

## Requirements and Usage

### Console version

`Python3` and additional packages: `pyperclip`, `sqlparse`

Run `python console_formatter.py C:path/to/your/index.R`
Add flag `-ndb` to replace old db names and alias to new ones.

### UI version

`Python3` and additional packages: `pyperclip`, `sqlparse`, `PyQt5`

Run `python sql_formatter.py` to start the app.


Left text window for input, right for output.


Format sql sqripts pushing **Beautify!** button `Ctrl+B`


Format R scripts by opening files pushing **Open R** button `Ctrl+O `


Format R scripts pasting to left window and pushing **BeautiFILE** button `Ctrl+Shift+B`


Text from right text window may be saved pushing **Save R** button `Ctrl+S`


Text from right text window may be saved to clipboard pushing **Copy to clipboard** button `Ctrl+Shift+C`


Highlight new DB names and alias with **Highlight** checkbox


To chage font use `Ctrl++` or `Ctrl+-`

## What formatter can do:

```
...BETWEEN DATE...
    ...AND DATE...
```

```
...JOIN...
...
...ON...
 ...AND...
```

```
...PARTITION BY column1,
                column2,
                column3
   ORDER BY ...
```

```
...CONCAT(SUBSTRING...
	   ...SUBSTRING...
	   ...SUBSTRING
```

## What formatter can't do:
Waiting for suggestions
