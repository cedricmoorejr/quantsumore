import re
import html as hhtml

class HTMLCleaner:
    def __init__(self):
        self.html_comment_pattern = re.compile(r'<!--.*?-->', flags=re.DOTALL)
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U0001F1E0-\U0001F1FF"  # Flags
            "]+", flags=re.UNICODE
        )
        self.newline_tab_pattern = re.compile(r'\\[ntr]|[\n\t\r]')
        self.space_pattern = re.compile(r'\s+')

    def remove_comments(self, html):
        return self.html_comment_pattern.sub('', html)

    def remove_emojis(self, text):
        return self.emoji_pattern.sub('', text)

    def decode(self, html):
        text = self.newline_tab_pattern.sub('', html)
        text = self.space_pattern.sub(' ', text).strip()
        decoded_text = hhtml.unescape(text)
        return decoded_text
       
    def __dir__(self):
        return ['remove_comments','remove_emojis', 'decode']


HTMLclean = HTMLCleaner()




def __dir__():
    return [
    'HTMLclean'    
    ]

__all__ = [
	'HTMLclean'
	]




