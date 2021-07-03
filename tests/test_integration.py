import pytest
import os
import PyPDF3
from pystitcher.stitcher import Stitcher
from itertools import chain

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"

TEST_DATA = [
    ("clean",6, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Volume 2', 3, 0), ('Part 2', 3, 1)]),
    ("keep",6, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Chapter 1', 0, 2), ('Chapter 2', 1, 2), ('Scene 1', 1, 3), ('Scene 2', 2, 3), ('Volume 2', 3, 0), ('Part 3', 3, 1), ('Chapter 3', 3, 2), ('Chapter 4', 4, 2), ('Scene 3', 4, 3), ('Scene 4', 5, 3)]),
    ("flatten", 6, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Chapter 1', 0, 2), ('Chapter 2', 1, 2), ('Scene 1', 1, 2), ('Scene 2', 2, 2), ('Volume 2', 3, 0), ('Part 3', 3, 1), ('Chapter 3', 3, 2), ('Chapter 4', 4, 2), ('Scene 3', 4, 2), ('Scene 4', 5, 2)]),
    ("rotate", 9, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Volume 2', 3, 0), ('Part 2', 3, 1), ('Volume 3', 6, 0), ('Part 3', 6, 1)]),
    ("min",3, [('Part 1', 0, 0), ('Chapter 1', 0, 1), ('Chapter 2', 1, 1), ('Scene 1', 1, 2), ('Scene 2', 2, 2)])
]

def pdf_name(name):
    return "tests/%s.pdf" % name

def render(name):
    input_file = open("tests/book-%s.md" % name, 'r')
    output_file = "%s.pdf" % name
    stitcher = Stitcher(input_file)
    stitcher.generate(output_file, True)
    # Switch back to main directory
    os.chdir(ROOT_DIR)
    return pdf_name(name)

def flatten_bookmarks(bookmarks, level=0):
    """Given a list, possibly nested to any level, return it flattened."""
    output = []
    for destination in bookmarks:
        if type(destination) == type([]):
            output.extend(flatten_bookmarks(destination, level+1))
        else:
            output.append((destination, level))
    return output

def get_all_bookmarks(pdf):
    """ Returns a list of all bookmarks with title, page number, and level in a PDF file"""
    bookmarks = flatten_bookmarks(pdf.getOutlines())
    return [(d[0]['/Title'], pdf.getDestinationPageNumber(d[0]), d[1]) for d in bookmarks]

@pytest.mark.parametrize("name,pages,bookmarks", TEST_DATA)
def test_book(name, pages, bookmarks):
    output_file = render(name)
    pdf = PyPDF3.PdfFileReader(output_file)
    assert pages == pdf.getNumPages()
    assert bookmarks == get_all_bookmarks(pdf)
    