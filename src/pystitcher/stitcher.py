import os
import markdown
from .bookmark import Bookmark
import html5lib
from PyPDF2 import PdfFileWriter, PdfFileReader
import subprocess
import tempfile
import logging

_logger = logging.getLogger(__name__)

""" Main Stitcher class """
class Stitcher:
    def __init__(self, inputBuffer):
        self.files = []
        self.currentPage = 1
        self.title = None
        self.bookmarks = []
        self.currentLevel = None
        self.oldBookmarks = []
        self.dir = os.path.dirname(os.path.abspath(inputBuffer.name))
        # TODO: This is a hack
        os.chdir(self.dir)

        text = inputBuffer.read()
        md = markdown.Markdown(extensions=['attr_list', 'meta'])
        html = md.convert(text)
        self.attributes = md.Meta

        document = html5lib.parseFragment(html, namespaceHTMLElements=False)
        for e in document.iter():
            self.iter(e)

    def _get_pdf_number_of_pages(self, filename):
        assert os.path.isfile(filename) and os.access(filename, os.R_OK), \
                "File {} doesn't exist or isn't readable".format(filename)
        pdf_reader = PdfFileReader(open(filename, "rb"))
        return pdf_reader.numPages

    def _getAttribute(self, key):
        return self.attributes.get(key, [None])[0]

    def iter(self, element):
        tag = element.tag
        b = None
        if(tag=='h1'):
            if (self.title == None):
                self.title = element.text
            b = Bookmark(self.currentPage, element.text, 1)
            self.currentLevel = 1
        elif(tag=='h2'):
            b = Bookmark(self.currentPage, element.text, 2)
            self.currentLevel = 2
        elif(tag =='h3'):
            b = Bookmark(self.currentPage, element.text, 3)
            self.currentLevel = 3
        elif(tag =='a'):
            file = element.attrib.get('href')
            b = Bookmark(self.currentPage, element.text, self.currentLevel+1)
            self.files.append((file, self.currentPage))
            # _logger.info("File: %s starts at %s", file, self.currentLevel)
            self.currentPage += self._get_pdf_number_of_pages(file)
        if b:
            self.bookmarks.append(b)

    def _add_bookmark(self, targetFileHandle, page, title, level):
        targetFileHandle.write("BookmarkBegin\n")
        targetFileHandle.write("BookmarkTitle: " + title + "\n")
        targetFileHandle.write("BookmarkLevel: " + str(level) + "\n")
        targetFileHandle.write("BookmarkPageNumber: " + str(page) + "\n")
        targetFileHandle.write("BookmarkZoom: FitHeight\n")

    def _existingBookmarkConfig(self):
        return self._getAttribute('existing_bookmarks')

    def _removeExistingBookmarks(self):
        return (self._existingBookmarkConfig() == 'remove')

    def _flattenBookmarks(self):
        return (self._existingBookmarkConfig() == 'flatten')

    def _generate_metadata(self, filename):
        with open(filename, 'w') as target:
            if (self.title):
                target.write("InfoBegin\n")
                target.write("InfoKey: Title\n")
                target.write("InfoValue: " + self.title + "\n")

            self.bookmarks.sort()

            bookmarks = self.bookmarks.copy()

            if (self._removeExistingBookmarks() != True):
                for b in self.oldBookmarks:
                    # _logger.info("Checking for %s(%s)", b.title, b.page+1)
                    outer_level = self._get_level_from_page_number(b.page+1)
                    # _logger.info("Got Level: %s", outer_level)
                    if (self._flattenBookmarks()):
                        increment = 1
                    else:
                        increment = b.level
                    level = outer_level + increment - 1
                    bookmarks.append(Bookmark(b.page+1, b.title, level))

            bookmarks.sort()
            self.bookmarks = bookmarks
            # self._print_bookmarks()
            for b in bookmarks:
                self._add_bookmark(target, b.page, b.title, b.level)

    def _print_bookmarks(self):
        for b in self.bookmarks:
            print((" " *( b.level-1)) + b.title + "("+str(b.page)+")")

    def _get_level_from_page_number(self, page):
        previousBookmarkLevel = self.bookmarks[0].level
        for b in self.bookmarks:
            # _logger.info("testing: %s (P%s) [L%s]", b.title, b.page, b.level)
            if (b.page > page):
                # _logger.info("Returning L%s", previousBookmarkLevel)
                return previousBookmarkLevel
            previousBookmarkLevel = b.level
        return previousBookmarkLevel

    def _iterate_old_bookmarks(self, pdf, startPage, bookmarks, level = 1):
        if (isinstance(bookmarks, list)):
            for inner_bookmark in bookmarks:
                self._iterate_old_bookmarks(pdf, startPage, inner_bookmark, level+1)
        else:
            localPageNumber = pdf.getDestinationPageNumber(bookmarks)
            globalPageNumber = startPage + localPageNumber - 1
            b = Bookmark(globalPageNumber, bookmarks.title, level)
            self.oldBookmarks.append(b)

    def _update_metadata(self, old_filename, metadata_file, outputFilename):
        currentBookmark = None
        # TODO: Code to add bookmarks natively
        # for b in self.bookmarks:
        #     if b.level >1:
        #         pass
        #     else:
        #         pass
        _logger.info("Running pdftkbox")
        subprocess.run(['java', '-jar', '/home/nemo/apps/PDFtkBox.jar', old_filename, 
            "update_info", metadata_file, 'output', outputFilename], capture_output=True)

    def _merge(self, output):
        writer = PdfFileWriter()
        for (inputFile,startPage) in self.files:
            assert os.path.isfile(inputFile), ERROR_PATH.format(inputFile)
            reader = PdfFileReader(open(inputFile, 'rb'))
            self._iterate_old_bookmarks(reader, startPage, reader.getOutlines())
            for page in range(1, reader.getNumPages()+1):
                writer.addPage(reader.getPage(page - 1))
    
        writer.write(output)
        output.close()

    def generate(self, outputFilename, cleanup = False):

        tempPdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tempMetadataFile = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)

        self._merge(tempPdf)
        self._generate_metadata(tempMetadataFile.name)
        self._update_metadata(tempPdf.name, tempMetadataFile.name, outputFilename)

        if (cleanup):
            _logger.info("Deleting temporary files")
            os.remove(tempMetadataFile.name)
            os.remove(tempPdf.name)
        else:
            print("Temporary files saved as ", tempPdf.name, tempMetadataFile.name)
