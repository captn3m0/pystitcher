import os
import logging
import shutil
import tempfile
import urllib.request
import validators

import html5lib
import markdown

from PyPDF3 import PdfFileWriter, PdfFileReader
from PyPDF3.generic import FloatObject
from pystitcher import __version__
from .bookmark import Bookmark

_logger = logging.getLogger(__name__)

""" Main Stitcher class """
class Stitcher:
    def __init__(self, inputBuffer):
        self.files = []
        self.currentPage = 1
        self.title = None
        self.bookmarks = []
        self.currentLevel = 0
        self.oldBookmarks = []
        self.dir = os.path.dirname(os.path.abspath(inputBuffer.name))
        # Fit complete page width by default
        DEFAULT_FIT = '/FitV'
        # Do not rotate by default
        DEFAULT_ROTATE = 0
        # Start at page 1 by default
        DEFAULT_START = 1
        # End at the final page by default
        DEFAULT_END = None

        # TODO: This is a hack
        os.chdir(self.dir)

        text = inputBuffer.read()
        md = markdown.Markdown(extensions=['attr_list', 'meta'])
        html = md.convert(text)
        self.attributes = md.Meta
        self.defaultFit = self._getAttribute('fit', DEFAULT_FIT)
        self.defaultRotate = self._getAttribute('rotate', DEFAULT_ROTATE)
        self.defaultStart = self._getAttribute('start', DEFAULT_START)
        self.defaultEnd = self._getAttribute('end', DEFAULT_END)

        document = html5lib.parseFragment(html, namespaceHTMLElements=False)
        for e in document.iter():
            self.iter(e)

    """
    Check if file has been cached locally and if
    not cached, download from provided URL. Return
    download filename
    """
    def _cacheURL(self, url):
        if not os.path.exists(os.path.basename(url)):
            _logger.info("Downloading PDF from remote URL %s", url)
            with urllib.request.urlopen(url) as response, open(os.path.basename(url), 'wb') as downloadedFile:
                shutil.copyfileobj(response, downloadedFile)
        else:
            _logger.info("Locally cached PDF found at %s", os.path.basename(url))
        return os.path.basename(url)

    """
    Get the number of pages in a PDF file
    """
    def _get_pdf_number_of_pages(self, filename):
        assert os.path.isfile(filename) and os.access(filename, os.R_OK), \
                "File {} doesn't exist or isn't readable".format(filename)
        pdf_reader = PdfFileReader(open(filename, "rb"))
        return pdf_reader.numPages

    """
    Return an attribute with a default value of None
    """
    def _getAttribute(self, key, default=None):
        return self.attributes.get(key, [default])[0]

    def _getMetadata(self):
        meta = {'/Producer': "pystitcher/%s" % __version__, '/Creator': "pystitcher/%s" % __version__}
        if (self._getAttribute('author')):
            meta["/Author"] = self._getAttribute('author')
        if (self._getAttribute('title')):
            meta["/Title"] = self._getAttribute('title')
        elif self.title:
            meta["/Title"] = self.title
        if (self._getAttribute('subject')):
            meta["/Subject"] = self._getAttribute('subject')
        if (self._getAttribute('keywords')):
            meta["/Keywords"] = self._getAttribute('keywords')

        return meta

    """
    Iterate through the elements in the spine HTML
    and generate self.bookmarks + self.files
    """
    def iter(self, element):
        tag = element.tag
        b = None
        if(tag=='h1'):
            if (self.title == None):
                self.title = element.text
            fit = element.attrib.get('fit', self.defaultFit)
            b = Bookmark(self.currentPage, element.text, 1, fit)
            self.currentLevel = 1
        elif(tag=='h2'):
            fit = element.attrib.get('fit', self.defaultFit)
            b = Bookmark(self.currentPage, element.text, 2, fit)
            self.currentLevel = 2
        elif(tag =='h3'):
            fit = element.attrib.get('fit', self.defaultFit)
            b = Bookmark(self.currentPage, element.text, 3, fit)
            self.currentLevel = 3
        elif(tag =='a'):
            file = element.attrib.get('href')
            if(validators.url(file)):
                file = self._cacheURL(file)
            fit = element.attrib.get('fit', self.defaultFit)
            rotate = int(element.attrib.get('rotate', self.defaultRotate))
            start = int(element.attrib.get('start', self.defaultStart))
            end = int(element.attrib.get('end', self._get_pdf_number_of_pages(file)
                                         if self.defaultEnd is None else self.defaultEnd))
            filters = (rotate, start, end)
            b = Bookmark(self.currentPage, element.text, self.currentLevel+1, fit)
            self.files.append((file, self.currentPage, filters))
            self.currentPage += (end - start) + 1
        if b:
            self.bookmarks.append(b)

    def _existingBookmarkConfig(self):
        EXISTING_BOOKMARKS_DEFAULT = 'remove'
        return self._getAttribute('existing_bookmarks', EXISTING_BOOKMARKS_DEFAULT)

    def _removeExistingBookmarks(self):
        return (self._existingBookmarkConfig() == 'remove')

    def _flattenBookmarks(self):
        return (self._existingBookmarkConfig() == 'flatten')

    """
    Adds the existing bookmarks into the
    self.bookmarks list
    """
    def _add_existing_bookmarks(self):
        self.bookmarks.sort()

        bookmarks = self.bookmarks.copy()

        if (self._removeExistingBookmarks() != True):
            for b in self.oldBookmarks:
                outer_level = self._get_level_from_page_number(b.page+1)
                if (self._flattenBookmarks()):
                    increment = 2
                else:
                    increment = b.level
                level = outer_level + increment - 1
                bookmarks.append(Bookmark(b.page+1, b.title, level, b.fit))

        bookmarks.sort()
        self.bookmarks = bookmarks

    """
    Gets the last bookmark level at a given page number
    on the combined PDF
    """
    def _get_level_from_page_number(self, page):
        previousBookmarkLevel = self.bookmarks[0].level
        for b in self.bookmarks:
            # _logger.info("testing: %s (P%s) [L%s]", b.title, b.page, b.level)
            if (b.page > page):
                # _logger.info("Returning L%s", previousBookmarkLevel)
                return previousBookmarkLevel
            previousBookmarkLevel = b.level
        return previousBookmarkLevel

    """
    Recursive method to read the old bookmarks (which are nested)
    and push them to self.oldBookmarks
    """
    def _iterate_old_bookmarks(self, pdf, startPage, bookmarks, level = 1):
        if (isinstance(bookmarks, list)):
            for inner_bookmark in bookmarks:
                self._iterate_old_bookmarks(pdf, startPage, inner_bookmark, level+1)
        else:
            localPageNumber = pdf.getDestinationPageNumber(bookmarks)
            globalPageNumber = startPage + localPageNumber - 1
            b = Bookmark(globalPageNumber, bookmarks.title, level, self.defaultFit)
            self.oldBookmarks.append(b)

    """
    Insert the bookmarks into the PDF file
    Ref: https://stackoverflow.com/a/18867646
    # TODO: Interleave this into the merge method somehow
    """
    def _insert_bookmarks(self, old_filename, outputFilename):
        stack = []
        pdfInput = PdfFileReader(open(old_filename, 'rb'))
        pdfOutput = PdfFileWriter()
        pdfOutput.cloneDocumentFromReader(pdfInput)
        for b in self.bookmarks:
            existingRef = None
            # Trim the stack till the top is useful (stack.level < b.level)
            while len(stack) > 0 and stack[len(stack)-1][0].level >= b.level:
                stack.pop()
            # If stack has something, use it
            if (len(stack) > 0):
                existingRef = stack[len(stack) - 1][1]
            bookmargArgs = [b.title, b.page-1, existingRef, None, False, False, b.fit] + b.cords
            stack.append((b, pdfOutput.addBookmark(*bookmargArgs)))
        pdfOutput.addMetadata(self._getMetadata())
        pdfOutput.write(open(outputFilename, 'wb'))

    """
    Merge the PDF files together in order
    and iterate through the old bookmarks
    as we're reading them
    """
    def _merge(self, output):
        writer = PdfFileWriter()
        for (inputFile,startPage,filters) in self.files:
            assert os.path.isfile(inputFile), ERROR_PATH.format(inputFile)
            reader = PdfFileReader(open(inputFile, 'rb'))
            # Recursively iterate through the old bookmarks
            self._iterate_old_bookmarks(reader, startPage, reader.getOutlines())
            rotate, start, end = filters
            for page in range(start, end + 1):
                writer.addPage(reader.getPage(page - 1).rotateClockwise(rotate))

        writer.write(output)
        output.close()

    """
    Main entrypoint to generate the final PDF
    """
    def generate(self, outputFilename, cleanup = False):
        tempPdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self._merge(tempPdf)
        # Only read the additional bookmarks if we're not removing them
        if (not self._removeExistingBookmarks()):
            self._add_existing_bookmarks()
        self._insert_bookmarks(tempPdf.name, outputFilename)

        if (cleanup):
            _logger.info("Deleting temporary files")
            os.remove(tempPdf.name)
        else:
            # Why print? Because this is not logging, this is output
            print("Temporary PDF file saved as ", tempPdf.name)
