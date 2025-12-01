import pandas as pd
from docx import Document
from pypdf import PdfReader
import io

import pandas as pd
from docx import Document
import io
import re
import pdfplumber

def read_file(uploaded_file):
    """
    Reads an uploaded file and returns a pandas DataFrame.
    Supports .xlsx, .csv, .docx, .pdf, and .txt files.
    """
    filename = uploaded_file.name
    if filename.endswith('.csv'):
        df = pd.read_csv(uploaded_file, skip_blank_lines=True)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif filename.endswith('.docx'):
        document = Document(uploaded_file)
        text = '\n'.join([para.text for para in document.paragraphs if para.text.strip() != ''])
        df = pd.read_csv(io.StringIO(text))
    elif filename.endswith('.pdf'):
        all_tables = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    all_tables.extend(table)
        if not all_tables:
            raise ValueError("No tables found in the PDF file.")

        # Assuming the first row of the first table is the header
        header = all_tables[0]
        data = all_tables[1:]
        df = pd.DataFrame(data, columns=header)
    elif filename.endswith('.txt'):
        text = uploaded_file.read().decode('utf-8')
        lines = text.splitlines()
        text = "\n".join([line for line in lines if line.strip()])
        df = pd.read_csv(io.StringIO(text))
    else:
        raise ValueError(f"Unsupported file format: {filename}")

    # Drop rows where all elements are NaN
    df.dropna(how='all', inplace=True)


    COLUMN_MAPPINGS = {
        'MPN': ['mpn', 'identified mpn'],
        'Quantity': ['quantity', 'qty'],
        'Reference Designator (Ref Des)': ['reference designator (ref des)', 'reference designators', 'ref des'],
        'Description': ['description', 'desc']
    }

    # Normalize column names
    # Create a copy to avoid SettingWithCopyWarning
    df_copy = df.copy()
    df_copy.columns = df_copy.columns.str.lower().str.strip()

    # Rename columns
    for standard_name, possible_names in COLUMN_MAPPINGS.items():
        for name in possible_names:
            if name in df_copy.columns:
                df_copy.rename(columns={name: standard_name}, inplace=True)
                break

    df = df_copy

    required_columns = ['MPN', 'Quantity', 'Reference Designator (Ref Des)', 'Description']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"File {filename} is missing one or more required columns. Found: {list(df.columns)}")

    # Ensure 'Quantity' column is numeric to prevent comparison errors
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0) # Fill NaN with 0 or handle as appropriate

    # Convert all other relevant columns to string type for consistent comparison
    for col in required_columns:
        if col != 'Quantity': # 'Quantity' is already handled as numeric
            df[col] = df[col].astype(str)

    return df

def compare_data(master_df, user_df):
    master_df = master_df.set_index('MPN')
    user_df = user_df.set_index('MPN')

    added = user_df.index.difference(master_df.index)
    removed = master_df.index.difference(user_df.index)

    common_mpns = master_df.index.intersection(user_df.index)
    master_common = master_df.loc[common_mpns]
    user_common = user_df.loc[common_mpns]

    # align columns before comparison
    user_common = user_common[master_common.columns]

    modified_mask = (master_common != user_common).any(axis=1)
    modified_mpns = modified_mask[modified_mask].index

    unchanged_mpns = common_mpns.difference(modified_mpns)

    return {
        'added': user_df.loc[added].reset_index().to_dict('records'),
        'removed': master_df.loc[removed].reset_index().to_dict('records'),
        'modified': [{
            'MPN': mpn,
            'master': master_df.loc[mpn].to_dict(),
            'user': user_df.loc[mpn].to_dict()
        } for mpn in modified_mpns],
        'unchanged': user_df.loc[unchanged_mpns].reset_index().to_dict('records')
    }
