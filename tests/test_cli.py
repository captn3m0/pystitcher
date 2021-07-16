from pystitcher.skeleton import parse_args
import logging

def test_default_args():
    args = parse_args(['tests/book-clean.md', 'o.pdf'])
    assert args.loglevel == None
    assert args.cleanup == True

def test_loglevel():
    args = parse_args(['-v', 'tests/book-clean.md', 'o.pdf'])
    assert args.loglevel == logging.INFO

def test_cleanup():
    args = parse_args(['--no-cleanup', 'tests/book-clean.md', 'o.pdf'])
    assert args.cleanup == False
