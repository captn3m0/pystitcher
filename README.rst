==========
pystitcher
==========


pystitcher stitches your PDF files together, generating nice customizable bookmarks for you using a declarative input file.


Description
===========

Given this input::

	existing_bookmarks: flatten
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

Configuration options can be specified with Meta data at the top of the file. These include:



.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.0.2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
