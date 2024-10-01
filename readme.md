# Pre-requisites

- homebrew
  - https://docs.brew.sh/Installation
- python 3.9.x (Latest commit of Detectron has issues with latest versions of python. Hence, it is recommended to install python 3.9.x)
  - ```brew install python```
  - https://docs.python-guide.org/starting/install3/osx/

# Setup all the dependencies
Once all the pre-requisites are installed, please follow setup.sh to install the dependencies.

```./setup.sh```

Please note that the shell script does not execute the python script.

# convert directory containing pdf, html/htm, docx files to JSON

convert_files_in_a_directory.py --directory <absolute_path_to_directory> --open_search_index_name <open_search_index_name> --document_url <document_url> --custom_column_config_file_path <absolute_path_to_config_file_with_custom_column_names>

### command line parameters
- directory - Absolute path to directory that contains pdf, html/htm, docx files to be loaded into open_search.
- open_search_index_name - open search index name in which the JSON is to be loaded.
- document_url(optional) - url of the document.
- custom_column_config_file_path(optional) - Sample of the custom column config file path is provided in sample_custom_column_config.txt. User will be prompted for all the custom columns.

# convert Atlassian confluence pages to JSON

atlassian_2_text.py --page_ids <page_ids> --api_token <api_token> --confluence_url <confluence_url> --open_search_index_name <open_search_index_name> --document_url <document_url> --custom_column_config_file_path <absolute_path_to_config_file_with_custom_column_names>

### command line parameters
- page_ids - Comma separated list of page_ids to be converted to open search compatible JSON's.
- api_token - api_token used to authenticate the api requests. Steps to fetch api token is documented in https://confluence.oci.oraclecorp.com/display/OCAS/Extract+data+from+confluence#Extractdatafromconfluence-3.FetchAPItokenfromconfluence.
- confluence_url - base url to confluence eg: https://confluence.oci.oraclecorp.com/
- open_search_index_name - open search index name in which the JSON is to be loaded.
- document_url(optional) - url of the pdf document.
- custom_column_config_file_path(optional) - Sample of the custom column config file path is provided in sample_custom_column_config.txt. User will be prompted for all the custom columns.