import re

class extract_company_name:
    def __init__(self, html):
        self.html = html
        self.name = self.extract_name()
        self.clean_company_name()

    def extract_name_from_html_1(self):
        start_tag = '<title>'
        end_tag = '</title>'
        start_pos = self.html.find(start_tag)
        end_pos = self.html.find(end_tag, start_pos)
        if start_pos != -1 and end_pos != -1:
            title_content = self.html[start_pos + len(start_tag):end_pos]
            company_name = title_content.split('(')[0].strip()
            return company_name
        return None

    def extract_name_from_html_2(self):
        title_pattern = r'<title>(.*?)\s*\(.*?</title>'
        match = re.search(title_pattern, self.html)
        if match:
            company_name = match.group(1).strip()
            return company_name
        return None

    def extract_name_from_html_3(self):
        meta_title_pattern = r'<meta\s+name="title"\s+content="(.*?)\s*\(.*?"'
        match = re.search(meta_title_pattern, self.html)
        if match:
            company_name = match.group(1).strip()
            return company_name
        return None
        
    def extract_name(self):
        for method in [self.extract_name_from_html_1, self.extract_name_from_html_2, self.extract_name_from_html_3]:
            name = method()
            if name:
                return name
        return None

    def clean_company_name(self):
        if self.name is not None:
            pattern = r'[\"\'\?\:\;\_\@\#\$\%\^\&\*\(\)\[\]\{\}\<\>\|\`\~\!\+\=\-\\\/\x00-\x1F\x7F]'
            cleaned_name = re.sub(pattern, '', self.name)
            cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
            self.name = cleaned_name.strip()
            
    def __dir__(self):
        return ['name']            
            
            
class market_find:
    def __init__(self, html):
        self.html = html
        self.market = None
        self._exchange_text = None
        self._extract_exchange_text()

    def _extract_exchange_text(self):
        start_tag = '<span class="exchange yf-1fo0o81">'
        end_tag = '</span>'
        
        start_index = self.html.find(start_tag)
        if start_index == -1:
            return
        
        # Move the index to the end of the start tag
        start_index += len(start_tag)
        
        # Find the closing span tag
        end_index = self.html.find(end_tag, start_index)
        if end_index == -1:
            return
        
        # Extract the inner HTML
        inner_html = self.html[start_index:end_index]
        
        # Remove nested tags to get the text
        text = self._remove_tags(inner_html)
        self._exchange_text = text.strip()
        self._tokenize_and_extract_market(self._exchange_text)

    def _remove_tags(self, html):
        inside_tag = False
        text = []
        for char in html:
            if char == '<':
                inside_tag = True
            elif char == '>':
                inside_tag = False
            elif not inside_tag:
                text.append(char)
        return ''.join(text)

    def _tokenize_and_extract_market(self, text):
        tokens = text.split()
        if tokens:
            self.market = tokens[0]
       
    def __dir__(self):
        return ['market']



def __dir__():
    return ['market_find', 'extract_company_name']

__all__ = ['market_find', 'extract_company_name']




