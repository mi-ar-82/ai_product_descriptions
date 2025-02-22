# File: tests/test_csv_processing.py

import unittest
from io import StringIO
import pandas as pd
from app.services.csv_validation import validate_csv_rows
from app.services.csv_parser import parse_csv
from pydantic import ValidationError

# Sample CSV content for testing
VALID_CSV_CONTENT = """Handle,Title,Body (HTML),Image Src,SEO Title,SEO Description
product-1,Product 1,<p>Body content</p>,http://example.com/image1.jpg,SEO Title 1,SEO Description 1
product-2,Product 2,<p>Another body</p>,http://example.com/image2.jpg,SEO Title 2,SEO Description 2
"""

INVALID_CSV_CONTENT = """Handle,Title,Body (HTML),Image Src,SEO Title
product-1,Product 1,<p>Body content</p>,http://example.com/image1.jpg,
"""

MISSING_COLUMN_CSV_CONTENT = """Handle,Title,Image Src,SEO Title,SEO Description
product-1,Product 1,http://example.com/image1.jpg,SEO Title 1,SEO Description 1
"""

EMPTY_CSV_CONTENT = """Handle,Title,Body (HTML),Image Src,SEO Title,SEO Description
"""


class TestValidateCSVRows(unittest.TestCase):
    def test_validate_csv_rows_valid_data(self):
        """
        Test that validate_csv_rows works correctly with valid data.
        """
        data = [
            {
                "Handle": "product-1",
                "Title": "Product 1",
                "Body (HTML)": "<p>Body content</p>",
                "Image Src": "http://example.com/image1.jpg",
                "SEO Title": "SEO Title 1",
                "SEO Description": "SEO Description 1",
            },
            {
                "Handle": "product-2",
                "Title": "Product 2",
                "Body (HTML)": "<p>Another body</p>",
                "Image Src": "http://example.com/image2.jpg",
                "SEO Title": "SEO Title 2",
                "SEO Description": "SEO Description 2",
            },
        ]
        validated_data = validate_csv_rows(data)
        self.assertEqual(len(validated_data), len(data))
        self.assertEqual(validated_data[0]["handle"], "product-1")
        self.assertEqual(validated_data[0]["input_title"], "Product 1")

    def test_validate_csv_rows_missing_fields(self):
        """
        Test that validate_csv_rows raises a ValueError for missing fields.
        """
        data = [
            {
                "Handle": "product-1",
                # Missing 'Title'
                "Body (HTML)": "<p>Body content</p>",
                "Image Src": "http://example.com/image1.jpg",
                "SEO Title": "SEO Title 1",
                "SEO Description": "SEO Description 1",
            }
        ]
        with self.assertRaises(ValueError) as context:
            validate_csv_rows(data)

        self.assertIn("missing required fields", str(context.exception))

    def test_validate_csv_rows_invalid_data(self):
        """
        Test that validate_csv_rows raises a ValidationError for invalid data types.
        """
        data = [
            {
                # Invalid 'Handle' type (should be a string)
                "Handle": None,
                "Title": "Product 1",
                "Body (HTML)": "<p>Body content</p>",
                "Image Src": "http://example.com/image1.jpg",
                "SEO Title": "SEO Title 1",
                "SEO Description": "SEO Description 1",
            }
        ]
        with self.assertRaises(ValueError):
            validate_csv_rows(data)


class TestParseCSV(unittest.TestCase):
    def test_parse_csv_valid_file(self):
        """
        Test that parse_csv works correctly with a valid CSV file.
        """
        csv_file = StringIO(VALID_CSV_CONTENT)
        df = parse_csv(csv_file)

        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["handle"], "product-1")
        self.assertEqual(df.iloc[0]["input_title"], "Product 1")

    def test_parse_csv_missing_columns(self):
        """
        Test that parse_csv raises a ValueError if required columns are missing.
        """
        csv_file = StringIO(MISSING_COLUMN_CSV_CONTENT)

        with self.assertRaises(ValueError) as context:
            parse_csv(csv_file)

        self.assertIn("Missing required columns", str(context.exception))

    def test_parse_csv_empty_file(self):
        """
        Test that parse_csv raises a ValueError for an empty CSV file.
        """
        csv_file = StringIO(EMPTY_CSV_CONTENT)  # Ensure this contains only headers and no rows

        with self.assertRaises(ValueError) as context:
            parse_csv(csv_file)

        self.assertIn("The provided CSV file is empty", str(context.exception))

    def test_parse_csv_invalid_data(self):
        """
        Test that parse_csv raises a ValueError if rows contain invalid data.
        """
        csv_file = StringIO(INVALID_CSV_CONTENT)

        with self.assertRaises(ValueError):
            parse_csv(csv_file)
