==========
pystitcher
==========

pystitcher stitches your PDF files together, generating nice customizable bookmarks for you using a declarative input in the form of a markdown file. It is written in pure python and uses `PyPDF3 <https://pypi.org/project/PyPDF3/>`_ for reading and writing PDF files.


Description
===========

Given this input::

	existing_bookmarks: flatten
	title: Complete Guide to the Personal Data Protection Bill
	author: Medianama
	keywords: privacy, surveillance, personal data protection
	subject: Personal Data Protection Bill
	# A Complete Guide to the Personal Data Protection Bill

	- [Cover](cover.pdf)

	# The Bills

	- [Personal Data Protection Bill, 2019](1.a.pdf)
	- [Personal Data Protection Bill, 2018](1.b.pdf)

	# Other key reading material

	- [Srikrishna Committee Report](2.a.pdf)
	- [Dvara Research's Personal Data Protection Bill](2.b.pdf)
	- [MP Shashi Tharoor's Data Protection Bill](2.c.pdf)
	- [MP Jay Panda's Data Protection Bill](2.d.pdf)
	- [SaveOurPrivacy.in bill](2.e.pdf)
	- [TRAI recommendations on privacy](2.f1.pdf)
	- [Comments on TRAI recommendations on privacy](2.f2.pdf)

Will generate a PDF with proper bookmarks:

.. image:: https://i.imgur.com/qPVpZGt.png

And the correct metadata::

	Title:          Complete Guide to the Personal Data Protection Bill
	Subject:        Personal Data Protection Bill
	Keywords:       privacy, surveillance, personal data protection
	Author:         Medianama
	Creator:        pystitcher/0.0.1
	Producer:       pystitcher/0.0.1

Configuration options can be specified with Meta data at the top of the file.

+---------------------+--------------------------------------------------------------------------+
| Option              | Notes                                                                    |
+=====================+==========================================================================+
| fit                 | Default fit of the bookmark. Can be overwritten per bookmark             |
|                     | See `Wiki <https://github.com/captn3m0/pystitcher/wiki/Zoom-Levels>`_    |
|                     | for more details.                                                        |
+---------------------+--------------------------------------------------------------------------+
| author              | PDF Author                                                               |
+---------------------+--------------------------------------------------------------------------+
| keywords            | PDF Keywords                                                             |
+---------------------+--------------------------------------------------------------------------+
| subject             | PDF Subject                                                              |
+---------------------+--------------------------------------------------------------------------+
| title               | PDF Title. If left unspecified, first Heading (h1)                       |
|                     | in the document is used.                                                 |
+---------------------+--------------------------------------------------------------------------+
| existing_bookmarks  | What to do with existing bookmarks in individual files.                  |
|                     | Options are ``keep``, ``flatten``, and ``remove``. See                   |
|                     | `Wiki <https://github.com/captn3m0/pystitcher/wiki/Existing-Bookmarks>`_ |
|                     | for more details.                                                        |
+---------------------+--------------------------------------------------------------------------+
