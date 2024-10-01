import os

from atlassian import Confluence
import argparse
from html_2_text import Convertor
from utils import util_methods

args_parser = argparse.ArgumentParser()
args_parser.add_argument("-p", "--page_ids", help="Comma separated list of page ID's", required=True)
args_parser.add_argument("-a", "--api_token", help="Api token used to authenticate to Atlassian", required=True)
args_parser.add_argument("-cu", "--confluence_url", help="confluence url for Atlassian eg:https://confluence.oci.oraclecorp.com/", required=True)
args_parser.add_argument("-o", "--open_search_index_name", help="Name of the open search index", required=True)
args_parser.add_argument("-c", "--custom_column_config_file_path", default="", help="url of the pdf document")

args = args_parser.parse_args()

page_ids = args.page_ids.replace(" ", "").split(",")
api_token = args.api_token
confluence_url = args.confluence_url
open_search_index_name = args.open_search_index_name
custom_column_config_file_path = args.custom_column_config_file_path

confluence = Confluence(url=confluence_url, token=api_token)

custom_columns = []

if custom_column_config_file_path != "":
    custom_columns = util_methods.fetch_custom_columns(custom_column_config_file_path)

for page_id in page_ids:
    page_info = confluence.get_page_by_id(page_id, expand='body.storage')
    page_title = page_info["title"]
    page_html = page_info['body']['storage']['value']

    markdown = Convertor(isMarkdown=True)
    res_markdown = markdown.get_parsed_output(page_html)

    node = {
        "title": page_title,
        "text": res_markdown,
        "url": f"{confluence_url}viewpage.action?pageId={page_id}"
    }

    for column in custom_columns:
        node.update(column)

    output = [node]

    util_methods.write_to_output_file(
        os.getcwd(),
        page_title,
        output,
        open_search_index_name
    )
