import os
import io

import PyPDF3
from pystitcher.stitcher import Stitcher
from pystitcher import __version__

import pytest
from contextlib import redirect_stdout

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"

"""
Fixtures for the integration tests. Each test is a tuple consisting of 4 things:
- input name (used as book-{name}.md)
- total expected page count
- A dictionary of expected metadata. Leave empty if nothing is set
- A flattened list of expected bookmarks, with each bookmark as a tuple containing:
  - Title
  - Destination Page Number
  - Bookmark Level (default = 0)
Each of the above 4 is passed to test_book as an argument
"""
TEST_DATA = [
    ("clean",6, {'Author': 'Wiki, the Cat', 'Title': 'Super Jelly Book', 'Subject': 'A book about adventures of Wiki, the cat.', 'Keywords': 'wiki,potato,jelly'}, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Volume 2', 3, 0), ('Part 2', 3, 1)]),
    ("keep",6, {'Title': 'Super Potato Book'}, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Chapter 1', 0, 2), ('Chapter 2', 1, 2), ('Scene 1', 1, 3), ('Scene 2', 2, 3), ('Volume 2', 3, 0), ('Part 3', 3, 1), ('Chapter 3', 3, 2), ('Chapter 4', 4, 2), ('Scene 3', 4, 3), ('Scene 4', 5, 3)]),
    ("flatten", 6, {}, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Chapter 1', 0, 2), ('Chapter 2', 1, 2), ('Scene 1', 1, 2), ('Scene 2', 2, 2), ('Volume 2', 3, 0), ('Part 3', 3, 1), ('Chapter 3', 3, 2), ('Chapter 4', 4, 2), ('Scene 3', 4, 2), ('Scene 4', 5, 2)]),
    ("rotate", 9, {}, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Volume 2', 3, 0), ('Part 2', 3, 1), ('Volume 3', 6, 0), ('Part 3', 6, 1)]),
    ("min",3, {}, [('Part 1', 0, 0), ('Chapter 1', 0, 1), ('Chapter 2', 1, 1), ('Scene 1', 1, 2), ('Scene 2', 2, 2)]),
    ("page-select", 9, {}, [('Super Potato Book', 0, 0), ('Volume 1', 0, 0), ('Part 1', 0, 1), ('Chapter 1', 0, 2), ('Chapter 2', 1, 2), ('Scene 1', 1, 3), ('Volume 2', 2, 0), ('Part 2', 2, 1), ('Scene 2', 2, 2), ('Chapter 3', 2, 2), ('Chapter 4', 3, 2), ('Scene 3', 3, 3), ('Volume 3', 4, 0), ('Part 3', 4, 1), ('Scene 4', 4, 2), ('Chapter 1', 4, 2), ('Chapter 2', 5, 2), ('Scene 1', 5, 3), ('Volume 4', 6, 0), ('Part 4', 6, 1), ('Scene 2', 6, 2), ('Chapter 3', 6, 2), ('Chapter 4', 7, 2), ('Scene 3', 7, 3), ('Scene 4', 8, 3)]),
    ("headings", 9, {'Title': 'Heading 1'}, [('Heading 1', 0, 0), ('Part 1', 0, 1), ('Heading 2', 3, 1), ('Part 2', 3, 2), ('Heading 3', 6, 2), ('Part 3', 6, 3)])
]

def pdf_name(name):
    return "tests/%s.pdf" % name

def render(name, cleanup=True):
    input_file = open("tests/book-%s.md" % name, 'r')
    output_file = "%s.pdf" % name
    stitcher = Stitcher(input_file)
    stitcher.generate(output_file, cleanup)
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

@pytest.mark.parametrize("name,pages,metadata,bookmarks", TEST_DATA)
def test_book(name, pages, metadata, bookmarks):
    output_file = render(name)
    pdf = PyPDF3.PdfFileReader(output_file)
    assert pages == pdf.getNumPages()
    assert bookmarks == get_all_bookmarks(pdf)
    info = pdf.getDocumentInfo()
    identity = "pystitcher/%s" % __version__
    assert identity == info['/Producer']
    assert identity == info['/Creator']
    for key in metadata:
        assert info["/%s" % key] == metadata[key]

def test_rotation():
    """ Validates the book-rotate.pdf with pages rotated."""
    output_file = render("rotate")
    pdf = PyPDF3.PdfFileReader(output_file)
    # Note that inputs to getPage are 0-indexed
    assert 90 == pdf.getPage(3)['/Rotate']
    assert 90 == pdf.getPage(4)['/Rotate']
    assert 90 == pdf.getPage(5)['/Rotate']
    assert 180 == pdf.getPage(6)['/Rotate']
    assert 180 == pdf.getPage(7)['/Rotate']
    assert 180 == pdf.getPage(8)['/Rotate']

def test_cleanup_disabled():
    f = io.StringIO()
    with redirect_stdout(f):
        output_file = render("min", False)
    temp_filename = f.getvalue()[29:-1]
    assert os.path.exists(temp_filename)
    pdf = PyPDF3.PdfFileReader(temp_filename)
    assert 3 == pdf.getNumPages()
    assert [] == pdf.getOutlines()
    # Clean it up manually to avoid cluttering
    os.remove(temp_filename)
