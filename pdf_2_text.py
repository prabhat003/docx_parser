import importlib
import json
import os
import pandas

from unstructured.partition.pdf import partition_pdf


def parse_pdf(pdf_file_path, document_url, index_name, custom_columns):
    if pdf_file_path.lower().endswith('.pdf'):
        print(f"Processing - {pdf_file_path}...")
        output_data_path = os.getcwd()
        pdf_file_path_arr = pdf_file_path.split("/")
        pdf_file_name = pdf_file_path_arr[-1]
        pdf_file_name_without_extension = pdf_file_name.rsplit('.', 1)[0]
        """if importlib.util.find_spec("detectron2") is None:
            raise Exception("infer_table_structure is true and detectron2 not installed")"""

        elements = partition_pdf(filename=pdf_file_path,
                                 strategy="hi_res",
                                 infer_table_structure=True
                                 )
        node = {}
        new_node = True
        node_text = []
        json_content = []
        last_page_number = 0

        # TODO: Merge common logic across multiple conversion python scripts
        for elem in elements:
            if elem.text.lower().startswith("copyright ©"):  # ignore copyright strings
                continue
            elif elem.category.lower() == "title":
                if new_node and len(node_text) == 0:
                    node = {"title": f"{pdf_file_name} - page_number {elem.metadata.page_number}"}
                    node_text.append(f"{elem.text}")
                    new_node = False
                else:  # new_node=False
                    if 'title' not in node:
                        node.update({"title": f"{pdf_file_name} - page_number {elem.metadata.page_number}"})
                    node.update({"text": "\n".join(node_text)})
                    node.update({"url": document_url})
                    node.update({"document_name": pdf_file_name})
                    node.update({"page_number": elem.metadata.page_number})
                    for column in custom_columns:
                        node.update(column)
                    json_content.append(node)
                    node_text = []
                    # For the Title that came in
                    node = {"title": f"{pdf_file_name} - page_number {elem.metadata.page_number}"}
                    node_text.append(f"{elem.text}")
            else:
                node_text.append(elem.text)
                # yolox and detectron2 has issues in parsing tables in pdfs. Hence, commenting it, needs revisit
                """
                if elem.category.lower() != "header" and elem.category.lower() != "footer":  # ignore header
                    if elem.metadata.text_as_html is not None:
                        df = pandas.read_html(elem.metadata.text_as_html)
                        text = "\n"
                        table_dict = df[0].fillna("").to_dict(orient="index")
                        two_d_array = []
                        for key, value in table_dict.items():
                            one_d_array = []
                            for table_dict_k, table_dict_v in value.items():
                                one_d_array.append(str(table_dict_v))
                            two_d_array.append(one_d_array)
                        for one_d_array in two_d_array:
                            text += one_d_array[0] + ":"
                            text += " | ".join(one_d_array)
                            text += "\n"
                        node_text.append(text)
                    else:
                        node_text.append(elem.text)"""

            last_page_number = elem.metadata.page_number

        if 'title' not in node:
            node.update({"title": f"{pdf_file_name} - page_number {last_page_number}"})
        node.update({"text": "\n".join(node_text)})
        node.update({"url": document_url})
        node.update({"document_name": pdf_file_name})
        node.update({"page_number": last_page_number})
        for column in custom_columns:
            node.update(column)
        json_content.append(node)

        os.makedirs(os.path.dirname(f"{output_data_path}/open_search_data/output.json"), exist_ok=True)
        with open(f"{output_data_path}/open_search_data/output_{pdf_file_name_without_extension}.json", "w") as f:
            for content in json_content:
                f.write(json.dumps({"index": {"_index": index_name}}) + '\n')
                f.write(json.dumps(content) + "\n")

        print(f"Processed {pdf_file_path}")
