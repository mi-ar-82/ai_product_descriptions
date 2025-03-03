# File: app/services/csv_validation.py
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


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
    validated_rows = []
    errors = []
    print(f"Debug: Validating {len(data)} rows of CSV data")

    print(type(enumerate(data)))
    for index, row in enumerate(data):
        print(type(index))
        print(type(row))
        try:
            validated_rows.append(ProductCSVRow.model_validate(row))
            print(f"Debug: Row {index} validated successfully")
        except ValidationError as e:
            logger.error(f"Row {index} validation failed: {e}")
            errors.append({
                "row": index,
                "errors": e.errors(),
                "input_data": row
            })
            print(f"Debug: Validation failed for row {index} with errors: {e.errors()}")

    if errors:
        raise ValueError(f"CSV validation failed with {len(errors)} errors")

    return validated_rows
