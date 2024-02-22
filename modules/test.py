from bs4 import Tag


class Test:
    name = ''
    message = ''
    stack_trace = ''

    def __init__(self, cols: list[Tag]):
        if len(cols) == 2:
            self.name = cols[1].text
            self.message = cols[0].text
        else:
            self.name = cols[0].text
            self.message = cols[3].text
            self.stack_trace = cols[4].text