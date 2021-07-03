import pytest
import os
import PyPDF3
from pystitcher.stitcher import Stitcher
from itertools import chain

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"

TEST_DATA = [
    ("clean",6, [('Super Potato Book', 0), ('Volume 1', 0), ('Part 1', 0), ('Volume 2', 3), ('Part 2', 3)]),
    ("keep",6, [('Super Potato Book', 0), ('Volume 1', 0), ('Part 1', 0), ('Chapter 1', 0), ('Chapter 2', 1), ('Scene 1', 1), ('Scene 2', 2), ('Volume 2', 3), ('Part 3', 3), ('Chapter 3', 3), ('Chapter 4', 4), ('Scene 3', 4), ('Scene 4', 5)]),
    ("flatten", 6, [('Super Potato Book', 0), ('Volume 1', 0), ('Part 1', 0), ('Chapter 1', 0), ('Chapter 2', 1), ('Scene 1', 1), ('Scene 2', 2), ('Volume 2', 3), ('Part 3', 3), ('Chapter 3', 3), ('Chapter 4', 4), ('Scene 3', 4), ('Scene 4', 5)]),
    ("rotate", 9, [('Super Potato Book', 0), ('Volume 1', 0), ('Part 1', 0), ('Volume 2', 3), ('Part 2', 3), ('Volume 3', 6), ('Part 3', 6)]),
    ("min",3, [('Part 1', 0), ('Chapter 1', 0), ('Chapter 2', 1), ('Scene 1', 1), ('Scene 2', 2)])
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

def flatten_bookmarks(bookmarks):
    """Given a list, possibly nested to any level, return it flattened."""
    output = []
    for destination in bookmarks:
        if type(destination) == type([]):
            output.extend(flatten_bookmarks(destination))
        else:
            output.append(destination)
    return output

def get_all_bookmarks(pdf):
    """ Returns a list of all flattened bookmarks with title and page number in a PDF file"""
    return [(d['/Title'], pdf.getDestinationPageNumber(d)) for d in flatten_bookmarks(pdf.getOutlines())]

@pytest.mark.parametrize("name,pages,bookmarks", TEST_DATA)
def test_book(name, pages, bookmarks):
    output_file = render(name)
    pdf = PyPDF3.PdfFileReader(output_file)
    assert pdf.getNumPages() == pages
    assert get_all_bookmarks(pdf) == bookmarks
    
