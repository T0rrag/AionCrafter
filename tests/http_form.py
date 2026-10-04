"""Submit the actual HTML form controls in HTTP acceptance tests (not visual QA)."""
from html.parser import HTMLParser


class FormControls(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.fields = {}
        self.select = self.option = self.textarea = None
        self.feed(html)

    def handle_starttag(self, tag, entries):
        attrs = dict(entries)
        if 'disabled' in attrs:
            return
        name = attrs.get('name')
        if tag == 'input' and name:
            kind = attrs.get('type', 'text')
            if kind not in ('submit', 'button', 'checkbox', 'radio') or (kind in ('checkbox', 'radio') and 'checked' in attrs):
                self.fields[name] = attrs.get('value', '')
        elif tag == 'textarea' and name:
            self.textarea = name
            self.fields[name] = ''
        elif tag == 'select' and name:
            self.select = name
        elif tag == 'option' and self.select:
            self.option = {'attrs': attrs, 'text': ''}

    def handle_data(self, text):
        if self.textarea:
            self.fields[self.textarea] += text
        if self.option is not None:
            self.option['text'] += text

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.textarea = None
        elif tag == 'option' and self.option is not None:
            attrs = self.option['attrs']
            if self.select not in self.fields or 'selected' in attrs:
                self.fields[self.select] = attrs.get('value', self.option['text'])
            self.option = None
        elif tag == 'select':
            self.select = None
