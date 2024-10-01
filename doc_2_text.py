import docx
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.text.hyperlink import Hyperlink
from docx.table import Table
import pandas as pd
from utils import util_methods


def fetch_content_with_hyperlinks(para):
    text = ""
    hyperlink = ""
    previous_paragraph_element = "text"
    for content in para.iter_inner_content():
        if isinstance(content, Run):
            if previous_paragraph_element == "url":
                if content.text.isspace():
                    text += content.text
                else:
                    text += f"[{hyperlink}]" + " "
                    hyperlink = ""
                    previous_paragraph_element = "text"
            else:
                previous_paragraph_element = "text"
            text += content.text

        elif isinstance(content, Hyperlink):
            text += content.text
            hyperlink = content.url
            previous_paragraph_element = "url"

    text += f"[{hyperlink}]" if hyperlink != "" else ""
    return text


def parse_docx(file_path, document_url, index_name, custom_columns):
    output_data_path, file_name, file_name_without_extension = util_methods.return_file_name_components(file_path)
    print(f"processing {file_name}...")
    document = docx.Document(file_path)

    heading_rank = {"heading1": 1, "heading2": 2, "heading3": 3, "heading4": 4, "heading5": 5, "heading6": 6}
    document_contents = document.iter_inner_content()
    node = {}
    node_text = []
    new_node = True
    output = []
    previous_element = ""
    heading_hierarchy_stack = []
    previous_dataframe = pd.DataFrame()
    dataframe = pd.DataFrame()
    title_text = ""

    # TODO: Merge common logic across multiple conversion python scripts
    for x in document_contents:
        if isinstance(x, Paragraph):
            if x.text != '' and x.text != '"' and x.text != "'":
                current_text_with_hyperlinks = fetch_content_with_hyperlinks(x)
                if previous_element != "paragraph" and previous_element != "":
                    table_markdown = previous_dataframe.to_markdown(index=False)
                    node_text.append(table_markdown + "\n")
                    previous_dataframe = pd.DataFrame()
                if x.style.name.lower() == "title":
                    title_text = current_text_with_hyperlinks + "\n"
                elif x.style.name.lower() != 'title':
                    if x.style.name.lower().startswith('heading'):
                        current_heading = x.style.name.lower().replace(" ", "")
                        if new_node:
                            node = {'title': f"{file_name}"}
                            new_node = False
                            heading_hierarchy_stack.append(
                                {
                                    "rank": heading_rank[current_heading],
                                    "text": current_text_with_hyperlinks
                                }
                            )
                        elif heading_rank[current_heading] > heading_hierarchy_stack[-1]["rank"]:
                            if len(node_text) > 0:
                                node.update({'text': title_text + heading_hierarchy_stack[-1][
                                    "text"] + "\n" + "\n".join(node_text)})
                                node.update({'url': document_url})
                                for column in custom_columns:
                                    node.update(column)
                                output.append(node)
                                node_text = []
                                node = {'title': f"{file_name}"}
                            heading_text = heading_hierarchy_stack[-1]["text"] + " - " + current_text_with_hyperlinks
                            heading_hierarchy_stack.append(
                                {
                                    "rank": heading_rank[current_heading],
                                    "text": heading_text
                                }
                            )
                        else:
                            node.update({'text': title_text + heading_hierarchy_stack[-1]["text"] + "\n" + "\n".join(
                                node_text)})
                            node.update({'url': document_url})
                            for column in custom_columns:
                                node.update(column)
                            output.append(node)
                            while len(heading_hierarchy_stack) != 0 and heading_rank[current_heading] <= \
                                    heading_hierarchy_stack[-1]["rank"]:
                                heading_hierarchy_stack.pop()
                            top_of_stack_text = heading_hierarchy_stack[-1]["text"] if len(
                                heading_hierarchy_stack) > 0 else ""
                            heading_text = top_of_stack_text + " - " + current_text_with_hyperlinks
                            heading_hierarchy_stack.append(
                                {
                                    "rank": heading_rank[current_heading],
                                    "text": heading_text
                                }
                            )
                            node_text = []
                            node = {'title': f"{file_name}"}
                    else:
                        node_text.append(current_text_with_hyperlinks + "\n")

                previous_element = "paragraph"
        if isinstance(x, Table):
            df = [['' for i in range(0, len(x.columns))] for j in range(len(x.rows))]

            for i, row in enumerate(x.rows):
                for j, cell in enumerate(row.cells):
                    df[i][j] = '' if (cell.text is None or cell.text == '') else cell.text

            dataframe = pd.DataFrame(df)

            if previous_element != "table":
                dataframe.columns = dataframe.iloc[0]
                dataframe = dataframe.drop(dataframe.index[0])
                previous_dataframe = dataframe
            else:
                if len(dataframe.columns) == len(previous_dataframe.columns):
                    dataframe.columns = previous_dataframe.columns
                    dataframe = pd.concat([previous_dataframe, dataframe], ignore_index=True)
                    previous_dataframe = dataframe
                else:
                    previous_table_markdown = dataframe.to_markdown(index=False)
                    previous_dataframe = dataframe
                    table_markdown = dataframe.to_markdown(index=False)

                    node_text.append(previous_table_markdown + "\n" + table_markdown + "\n")

            previous_element = "table"

    table_markdown = previous_dataframe.to_markdown(index=False)
    node_text.append(table_markdown + "\n")
    top_of_stack_text = heading_hierarchy_stack[-1]["text"] if len(
        heading_hierarchy_stack) > 0 else ""
    node.update({'text': title_text + top_of_stack_text + " - " + "\n".join(node_text)})
    node.update({'url': document_url})
    for column in custom_columns:
        node.update(column)
    output.append(node)

    util_methods.write_to_output_file(output_data_path, file_name_without_extension, output, index_name)

    print(f"processed {file_name}")
