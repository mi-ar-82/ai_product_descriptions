from pydantic import BaseModel, ValidationError
from typing import List, Dict


# Define the Pydantic model for validation
class ProductCSVRow(BaseModel):
    handle: str
    input_title: str
    input_body: str
    input_image: str
    input_seo_title: str
    input_seo_descr: str


def validate_csv_rows(data: List[Dict]) -> List[Dict]:
    """
    Validate rows in the CSV file using Pydantic.

    Args:
        data (List[Dict]): List of rows (dictionaries) from the CSV file.

    Returns:
        List[Dict]: Validated rows.

    Raises:
        ValueError: If a row fails validation.
    """
    validated_rows = []
    errors = []

    required_keys = ['Handle', 'Title', 'Body (HTML)', 'Image Src', 'SEO Title', 'SEO Description']

    for index, row in enumerate(data):
        # Check for missing keys
        missing_keys = [key for key in required_keys if key not in row]
        if missing_keys:
            raise ValueError(f"Row {index} is missing required fields: {missing_keys}")

        try:
            # Validate each row using the Pydantic model
            validated_row = ProductCSVRow(
                handle=row['Handle'],
                input_title=row['Title'],
                input_body=row['Body (HTML)'],
                input_image=row['Image Src'],
                input_seo_title=row['SEO Title'],
                input_seo_descr=row['SEO Description']
            )
            validated_rows.append(validated_row.dict())
        except ValidationError as e:
            errors.append({"row_index": index, "errors": e.errors()})

    if errors:
        raise ValueError(f"Validation errors occurred: {errors}")

    return validated_rows
