# Prompts Used to Create the Project

This document contains a compilation of all the prompts provided by the user throughout the project creation process.

---

## Initial Project Request

> Role: Python django developer Requirement: I want to create a python django project of bom comparison tool. i explian step by step requirment. 1. create a venv of python (3.12) 2.
  create a one folder along with venv 'bom_comp', and that folder in create a django project 'bom_comparision'. then create a app 'core'. 2. Project workflow define below  a. User
  upload a BOM file in xlsx, csv, docx, pdf, txt any of this format and this file compate aginst master BOM file. b. both file select after user can compare this two file (provide a
  compare button). c. after compare button workflow both file read in backend and comapare files (Master BOM file aginst user selected file. compare fields like this must be follow
  (MPN, Quantity, Reference Designator (Ref Des), Description and if other columns are mathched then also that columns comapre. d. after comapre two files both files data render in UI
  and detected differences show in diffrent colour (UI like this both files show in diffrnet  table - master bom show in left side table and other file show in right side table.  Rules:
  1. add usefull comment in code. 2. generate  a test case for code. 3. following gidelines of python django code blow a. starnded nameing of varialbe b. using function base view c. UI
  in use bootstarp.  create a project for above prompt.

---

## Prompt 2: Column Name Flexibility

> Great! now issue is proejct check specific column names like i explian in first prompt. but i user uploaded file in not specific columns name 'MPN' , etc.. i provide a sample files
  location is @bom_comp/bom_samples/ this folder in files avialable (all format .pdf , .xlxs, .dox, .csv) so following files related make changes and files in ingore blank lines.

---

## Prompt 3: PDF Reading and UI Improvement (Initial)

> Great works for .csv , .xlxs not working on .pdf file getting error in read. first need to improve UI logic below a. user selecte tow file its is okay and working fine!! after compers
  files then i want to redirect in another page and show proper two tables with overflow sroll, and diffrent deteteded show in diff color columns, like added records show in green
  color, deleted row light red, and modified records in light brown.

---

## Prompt 4: UI Improvement (Single Table with Colors)

> working okay. now i want to user-interface to used (userfriendy) make UI like useing bootstrap color use for added rows for green color apply in row and deleted row for apply red
  color and modified row for brown color apply in row and not creating a diffrent tables for add , delete and modified row vise all add show in one table for particuler file. apply
  color in row for highlight and this color box define in right side top for this color use for this modification.

---

## Prompt 5: UI Improvement (Two Tables, Download JSON)

> following steps: 1. compare page in show two tables for master and other file other file in highlight row for add, updated and deleted row. 2. provide a 'download json' button in
  compare page in right top side and compare file download in json foramte.

---

## Prompt 6: Type Error during Comparison (Initial)

> follwing issue face in comapare time '<' not supported between instances of 'float' and 'str' so repars all comapre code.

---

## Prompt 7: Type Error during Comparison (MPN, All Columns)

> follwing issue face in comapare time '<' not supported between instances of 'float' and 'str' so repars all comapre code. for all coloums.  user_bom_for_display.sort(key=lambda x:
  x.get('MPN', '')) this line thourgh  error  note: mpn type also float, int, str and other columns also check type i suggest a convert str type and then check all columns.

---

## Prompt 8: Django Template Underscore Error

> html file in 'user_bom_for_display' in key name getting error beacuse key name starting with _. 'Variables and attributes may not begin with underscores: 'row._status''

---

## Prompt 9: Store in DB, Home Page Listing, View Button

> now followng steps: 1. user uploaded both file store in db and read data also save in db. and that data show in home page like listing table. table column name master_file, user_file, view buttton. 2. view button on click redirect comapre page and show both table.

---

## Prompt 10: JSONField Check Constraint Error

> An error occurred: CHECK constraint failed: (JSON_VALID("master_data") OR "master_data" IS NULL)

---

## Prompt 11: PDF Reading Error (No Tables)

> now pdf reading in error: An error occurred: Error reading file bom - master.pdf: No tables found in the PDF file.

---

## Prompt 12: PDF Reading Error (Tokenizing Data)

> .pdf in getting error not read proper and error: compare_boms function error: Error reading file bom - master.pdf: Could not extract tables or parse text from PDF: Error tokenizing data. C error: Expected 1 fields in line 4, saw 3

---

## Prompt 13: PDF Reading Error (Missing Required Columns)

> An error occurred: Error reading file bom - master.pdf: File bom - master.pdf is missing one or more required columns. Found: ['identified']

---
## Prompt 14: Create prompt_ai.md

> crate a all prompt i used for create a project that all prompt store in prmopt_ai.md file in root derectory
