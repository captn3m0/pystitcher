""" Bookmark class """
class Bookmark:
    def __init__(self, page, title, level=1, fit='/FitV'):
        self.page = page
        self.title = title
        self.level = level
        # default value for now
        self.fit = fit
        if (self.fit == '/Fit' or self.fit == '/FitB'):
            self.cords = []
        elif (self.fit == '/FitH' or self.fit == '/FitV' or self.fit == '/FitBH' or self.fit == '/FitBV'):
            self.cords = [(0)]
        else:
            self.fit = '/FitB'
            self.cords = []


    def __lt__(self, other):
         return self.page < other.page

    def __repr__(self):
        return str([self.page, self.title, self.level])
