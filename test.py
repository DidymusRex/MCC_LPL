#!/usr/bin/env python
# ------------------------------------------------------------------------------
# file: test.py
# desc: print test for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------
from escpos import *
import time
import uuid

# ------------------------------------------------------------------------------
def test_printer():
        p.set(align='LEFT', font='A', width=1, height=1)
        p.text('Font A max chars 33\n')
        p.text("----.----0----.----0----.---0---\n")
        p.text(time.strftime('%a %b %d %Y %r\n'))

        p.set(align='LEFT', font='B', width=1, height=1)
        p.text('Font B max chars 44\n')
        p.text("----.----0----.----0----.---0----.---0----\n")
        p.text(time.strftime('%a %b %d %Y %r\n'))

        p.set(align='CENTER')
        v = '2695880042000'
        p.barcode(v, 'EAN13', 64, 2, 'OFF', 'B')
        p.text(v)

        v=str(uuid.uuid4())
        p.qr(v, size=6)
        p.text(v)

# ------------------------------------------------------------------------------
def print_lottery():
    # Faux lottery ticker
        # Print the logo
        p.image("images/mpz_logo.jpg")

        p.set(align='RIGHT', font='B', width=1, height=1)

        # Numbersmig0hurz-yoga

        p.set(align='RIGHT', font='B', width=1, height=1)
        p.text("==========================================\n")
        p.text("Extra\n")

        p.set(align='CENTER', font='B', width=2, height=2)
        p.text("A.00 00 00 00 00   00\n")
        p.text("B.00 00 00 00 00   00\n")
        p.text("C.00 00 00 00 00   00\n")
        p.text("D.00 00 00 00 00   00\n")
        p.text("E.00 00 00 00 00   00\n")
        p.text("F.00 00 00 00 00   00\n")
        p.text("G.00 00 00 00 00   00\n")
        p.text("H.00 00 00 00 00   00\n")
        p.text("I.00 00 00 00 00   00\n")
        p.text("J.00 00 00 00 00   00\n")

        p.set(align='RIGHT', font='B', width=1, height=1)
        p.text("==========================================\n")

        p.set(align='CENTER')
        p.text(time.strftime('%a %b %d %Y %r\n'))
        # Print a barode for value v
        # v = '2695880042000'
        # p.barcode(v, 'EAN13', 64, 2, 'OFF', 'B')

        # Print a QR Code for value v
        v=str(uuid.uuid4())
        p.qr(v, size=6)
        p.text(v)

# ------------------------------------------------------------------------------
def library_header():
        # Library Logo
        p.image('images/MCCL_Logo.png')
        p.set(align='LEFT', font='A', width=1, height=1)

        p.text('Miscatonic Community College\n')
        p.set(align='CENTER', width=2, height=2)
        p.text('Library\n')

# ------------------------------------------------------------------------------
def print_book_info(title, author, isbn):
        library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text('\nTitle:')
        p.text(title)        
        p.text('\nAuthor:')
        p.text(author)
        p.text('\nISBN:')
        p.text(isbn)
        p.text('\n\n')
        p.barcode(isbn, 'EAN13', 64, 3, 'OFF', 'A' )
        p.set(align='LEFT', font='A', width=1, height=1)
        p.text('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')

# ------------------------------------------------------------------------------
def main():
        p.hw('INIT')

        test_printer()
        print_lottery()
        print_book_info('The Lord of the Rings', 'J.R.R. Tolkien', '9780544003415')

        p.cut()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == "__main__":
        # Configure Printer
        printer_type="Usb"
        printer_vendor=0x28e9
        printer_product=0x0289
        printer_interface=0
        printer_in_ep=0x81
        printer_out_ep=0x03
        printer_profile="simple"

        p = printer.Usb(printer_vendor,
                printer_product,
                printer_interface,
                printer_in_ep,
                printer_out_ep)

        main()
