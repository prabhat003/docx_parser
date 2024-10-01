import re
import html2text
from bs4 import BeautifulSoup
from utils import util_methods

# TODO: Maintain header context
class Cleaner:
    def __init__(self):
        self.soup = None
        self.title = None

    # remove js/css tags
    def _remove_redundant_tags(self):
        for tag in self.soup(['script', 'style', 'aside']):
            tag.decompose()

            # remove based on phrases, for fallback in case of problems

    def _remove_on_fallback(self, data):
        # left side bar
        regex_pattern = r"[a-zA-Z]kip.*[a-zA-Z]ontent"
        match = re.search(regex_pattern, data)
        if match:
            data = data[match.end():]

        # right side bar
        regex_pattern = [r"[wW]as.*[hH]elpful?", r"(Copyright|©).*Oracle", r"Resources for.*", \
                         r"Why Oracle", r"News and Events", r"Contact Us", \
                         r"Previous Page", r"Related Content", r"More Resources"]
        for pattern in regex_pattern:
            idx = re.search(pattern, data)
            if idx:
                data = data[:idx.start()]

        return data

    # remove header
    def _remove_header(self):
        for tag in self.soup(['header', "nav"]):
            tag.decompose()

            # remove footer

    def _remove_footer(self):
        for tag in self.soup(['footer']):
            tag.decompose()

    def __get_section_names(self):
        sections = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5','h6'])
        headings = [section.text for section in sections]
        return headings

    def __get_sections(self, data):
        # The first is the before any heading part so not required
        return re.split('<h\d', data)[1:]

    # remove side bars
    def _remove_side_bars(self):
        # find the headings in the html
        headings = self.__get_section_names()
        # Divide the html based on headings and find title idx in these headings
        title_idx = headings.index(self.title) if self.title in headings else 0
        # Take only part of html which is after the title is used as a heading
        headings_under_consideration = headings[title_idx:]
        sections = self.__get_sections(str(self.soup))[title_idx:]
        return sections

    def _remove_tables(self):
        # remove tables
        for tag in self.soup(['table']):
            tag.decompose()

    def _clean_html(self):
        self._remove_redundant_tags()
        self._remove_footer()
        self._remove_header()
        sections = self._remove_side_bars()
        return sections


class Convertor(Cleaner):
    def __init__(self, isMarkdown=True):
        super().__init__()
        self.isMarkdown = isMarkdown
        self.markdown = html2text.HTML2Text()
        self.markdown.MARK_CODE = True
        self.markdown.body_width = 0
        self.markdown.SINGLE_LINE_BREAK = True
        if not isMarkdown:
            self.markdown.IGNORE_ANCHORS = True
            self.markdown.IGNORE_MAILTO_LINKS = True
            self.markdown.IGNORE_IMAGES = True
            self.markdown.IGNORE_TABLES = True
            self.markdown.ignore_links = True
            self.markdown.IGNORE_EMPHASIS = True
            self.markdown.strong_mark = ""
            self.markdown.emphasis_mark = ""

    def _parse_html(self):
        res = []
        for section in self.sections:
            idx = section.find(">")
            if idx:
                section = section[idx + 1:]
            res.append(self.markdown.handle(section))
        res = "".join(res)
        res = self._remove_on_fallback(res)
        res = re.sub(r'\n\n+', r'\n\n', res)
        res = re.sub(r'^\n+', '', res)
        return res

    def apply(self, webpage):
        file = open(webpage, "r")
        html = file.read()
        return self.get_parsed_output(html)

    def get_parsed_output(self, html):
        # convert to soup
        self.soup = BeautifulSoup(html, "html.parser")
        self.title = self.soup.title.string if self.soup.title else None
        if not self.isMarkdown:
            self._remove_tables()
        self.sections = self._clean_html()
        res = self._parse_html()
        return res


def parse_html_2_text(file_path, document_url, index_name, custom_columns):
    output_data_path, file_name, file_name_without_extension = util_methods.return_file_name_components(file_path)
    markdown = Convertor(isMarkdown=True)
    res_markdown = markdown.apply(file_path)
    node = {
            "title": file_name,
            "text": res_markdown,
            "url": document_url
    }
    for column in custom_columns:
        node.update(column)
    output = [node]
    util_methods.write_to_output_file(output_data_path, file_name_without_extension, output, index_name)
