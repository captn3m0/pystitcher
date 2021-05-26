""" Bookmark class """
class Bookmark:
    def __init__(self, page, title, level=1):
        self.page = page
        self.title = title
        self.level = level

    def __lt__(self, other):
         return self.page < other.page

    def __repr__(self):
        return str([self.page, self.title, self.level])