import os
import argparse
import doc_2_text
import pdf_2_text
import html_2_text
import pptx_to_json_extractor
from utils import util_methods

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="Absolute path of the folder containing pdf, html/htm, docx documents", required=True)
parser.add_argument("-o", "--open_search_index_name", help="Name of the open search index", required=True)
parser.add_argument("-u", "--document_url", default="", help="url of the pdf document")
parser.add_argument("-c", "--custom_column_config_file_path", default="", help="url of the pdf document")

args = parser.parse_args()
directory = args.directory
open_search_index = args.open_search_index_name
document_url = args.document_url
custom_column_config_file_path = args.custom_column_config_file_path

custom_columns = []

if custom_column_config_file_path != "":
    custom_columns = util_methods.fetch_custom_columns(custom_column_config_file_path)

for dirpath, _, filenames in os.walk(directory):
    for f in filenames:
        file_path = os.path.abspath(os.path.join(dirpath, f))
        if file_path.lower().endswith(".pdf"):
            pdf_2_text.parse_pdf(file_path, document_url, open_search_index, custom_columns)
        elif file_path.lower().endswith(".html") or file_path.lower().endswith(".htm"):
            html_2_text.parse_html_2_text(file_path, document_url, open_search_index, custom_columns)
        elif file_path.lower().endswith(".docx"):
            doc_2_text.parse_docx(file_path, document_url, open_search_index, custom_columns)
        elif file_path.lower().endswith("pptx"):
            pptx_to_json_extractor.parse_pptx(file_path, document_url, open_search_index, custom_columns)
        else:
            print(f"file - {file_path} will be ignored since its not pdf, html/htm, docx format")

# TODO: Upload the JSON's to opensearch index
