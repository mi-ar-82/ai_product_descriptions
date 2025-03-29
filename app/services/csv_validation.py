# File: app/services/csv_validation.py
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict



class ProductCSVRow(BaseModel):
    handle: str = Field(..., alias = "Handle")
    input_title: str = Field(..., alias = "Title")
    input_body: str = Field(..., alias = "Body (HTML)")
    input_image: str = Field(..., alias = "Image Src")
    input_seo_title: str = Field(..., alias = "SEO Title")
    input_seo_descr: str = Field(..., alias = "SEO Description")

    class Config:
        populate_by_name = True


def validate_csv_rows(data: List[Dict]) -> List[ProductCSVRow]:
    """

    :rtype: object
    """
    validated_rows = []
    errors = []
    print(f"Debug: Validating {len(data)} rows of CSV data")

    print(type(enumerate(data)))
    for index, row in enumerate(data):
        print(f"Debug: Validating row {index}, type: {type(row)}")
        print(type(index))
        print(type(row))
        try:
            validated_rows.append(ProductCSVRow.model_validate(row))
            print(f"Debug: Row {index} validated successfully")
        except ValidationError as e:
            print(f"Debug: Validation failed for row {index} with errors: {e.errors()}")

    if errors:
        raise ValidationError(f"CSV validation failed with {len(errors)} errors")

    return validated_rows
