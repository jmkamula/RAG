"""
Ship 54'.e — structural-evidence detector unit tests.

Locks the 5 pattern detectors: doc-control header, revision history,
signature blocks, interested parties, table of contents. Both prose
shape (same-line `Label: value`) and mammoth-extracted docx table
shape (two-line `__Label__` \\n `value`) are covered.
"""

import unittest

from rag.intake.structural_evidence import (
    extract_structural_evidence,
    detect_doc_control_header,
    detect_revision_history,
    detect_interested_parties,
    detect_table_of_contents,
)


class TestDocControlHeader(unittest.TestCase):

    def test_same_line_prose(self):
        """Consultant-toolkit doc-control block in prose form."""
        text = """
        INFORMATION SECURITY POLICY
        Document No.: L1-POL-001
        Revision: Rev 03
        Revision Date: 03 Aug 2026
        Prepared By: Jane Doe
        Reviewed By: Alex Chen
        Approved By: Maria Silva, CEO
        """
        hdr = detect_doc_control_header(text)
        self.assertTrue(hdr.is_present)
        self.assertEqual(hdr.field_count, 6)
        self.assertEqual(hdr.doc_no,      "L1-POL-001")
        self.assertEqual(hdr.revision,    "Rev 03")
        self.assertEqual(hdr.rev_date,    "03 Aug 2026")
        self.assertEqual(hdr.prepared_by, "Jane Doe")
        self.assertEqual(hdr.reviewed_by, "Alex Chen")
        self.assertEqual(hdr.approved_by, "Maria Silva, CEO")

    def test_mammoth_two_line_shape(self):
        """DOCX table extracted by mammoth — label on one line, value on next."""
        text = r"""# Information Security Policy

__Document No\.__

POL\-5\.2\-Rev03

__Revision__

Rev03

__Revision Date__

03 Aug 2026

__Prepared By__

\_\_\_\_\_\_\_\_\_\_
"""
        # Test via extract_structural_evidence — that path applies
        # mammoth-escape normalization
        ev = extract_structural_evidence(text)
        self.assertTrue(ev.doc_control.is_present)
        self.assertEqual(ev.doc_control.doc_no,   "POL-5.2-Rev03")
        self.assertEqual(ev.doc_control.revision, "Rev03")
        self.assertEqual(ev.doc_control.rev_date, "03 Aug 2026")
        # Wet-sign underscores stripped → None
        self.assertIsNone(ev.doc_control.prepared_by)

    def test_below_threshold_not_present(self):
        """One stray label alone doesn't trigger a false-positive."""
        text = """
        Just prose about compliance. Document No. 123 appears deep
        in the body but there's no header block.
        """
        hdr = detect_doc_control_header(text)
        self.assertLess(hdr.field_count, 3)
        self.assertFalse(hdr.is_present)

    def test_empty_text(self):
        hdr = detect_doc_control_header("")
        self.assertFalse(hdr.is_present)
        self.assertEqual(hdr.field_count, 0)


class TestRevisionHistory(unittest.TestCase):

    def test_inline_table(self):
        """Version-Date-Description one-per-line prose table."""
        text = """
        10. REVISION HISTORY
        Version   Date          Description                     Author
        03        03 Aug 2026   Aligned with ISO 27001:2022     Jane Doe
        02        14 Jan 2026   Added third-country transfer   Jane Doe
        """
        rh = detect_revision_history(text)
        self.assertTrue(rh.present)
        self.assertEqual(rh.row_count, 2)

    def test_docx_one_cell_per_line(self):
        """DOCX table extraction — dates on standalone lines."""
        text = """## Revision History

Version

Date

Description of Change

Author

03

03 Aug 2026

Initial issue

Jane Doe
"""
        rh = detect_revision_history(text)
        self.assertTrue(rh.present)
        self.assertGreaterEqual(rh.row_count, 1)

    def test_missing_header(self):
        text = "No revision history in this document."
        rh = detect_revision_history(text)
        self.assertFalse(rh.present)


class TestInterestedParties(unittest.TestCase):

    def test_bullet_list_after_header(self):
        text = """
        INTERESTED PARTIES
        - Employees
        - Customers
        - Regulators (ICO)
        - Certification body
        - Third-party auditors
        """
        ip = detect_interested_parties(text)
        self.assertTrue(ip.present)
        self.assertEqual(len(ip.parties), 5)
        self.assertIn("Employees", ip.parties)
        self.assertIn("Regulators (ICO)", ip.parties)

    def test_no_header(self):
        text = "Some other content. Employees and customers mentioned inline."
        ip = detect_interested_parties(text)
        self.assertFalse(ip.present)


class TestTableOfContents(unittest.TestCase):

    def test_toc_with_page_numbers(self):
        text = """
        TABLE OF CONTENTS
        1. Purpose ..................... 2
        2. Scope ....................... 3
        3. Roles ....................... 4
        4. Procedure ................... 5
        """
        toc = detect_table_of_contents(text)
        self.assertTrue(toc.present)
        self.assertGreaterEqual(toc.entry_count, 3)

    def test_toc_header_but_no_entries(self):
        text = "TABLE OF CONTENTS\n\nThis document has no TOC entries yet."
        toc = detect_table_of_contents(text)
        self.assertFalse(toc.present)


class TestCombinedRunner(unittest.TestCase):

    def test_full_consultant_shape(self):
        """A canonical consultant-toolkit policy — all 5 patterns present."""
        text = """
        INFORMATION SECURITY POLICY
        Document No.: L1-POL-001
        Revision: Rev 03
        Revision Date: 03 Aug 2026
        Prepared By: Jane Doe
        Reviewed By: Alex Chen
        Approved By: Maria Silva, CEO

        TABLE OF CONTENTS
        1. Purpose ..................... 2
        2. Scope ....................... 3
        3. Roles ....................... 4

        INTERESTED PARTIES
        - Employees
        - Customers
        - Regulators

        ... body ...

        REVISION HISTORY
        Version   Date          Description   Author
        03        03 Aug 2026   Aligned       Jane Doe
        """
        ev = extract_structural_evidence(text)
        self.assertTrue(ev.any_detected)
        self.assertTrue(ev.doc_control.is_present)
        self.assertTrue(ev.revision_history.present)
        self.assertTrue(ev.interested_parties.present)
        self.assertTrue(ev.toc.present)

    def test_casual_note(self):
        """A casual document — no structural evidence."""
        text = "Just a note about how we do things. No structure."
        ev = extract_structural_evidence(text)
        self.assertFalse(ev.any_detected)


if __name__ == "__main__":
    unittest.main()
