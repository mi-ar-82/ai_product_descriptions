import pandas as pd
from app.services.csv_validation import validate_csv_rows

def parse_csv(file_path: str) -> pd.DataFrame:
    """
    Parse and validate a CSV file using Pandas and Pydantic.

    Args:
        file_path (str): Path to the uploaded CSV file.

    Returns:
        pd.DataFrame: DataFrame containing validated data.

    Raises:
        ValueError: If required columns are missing, validation fails, or the file is empty.
    """
    print(f"Debug: Parsing CSV file from path: {file_path}")
    # Load the CSV into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("The provided CSV file is empty.")

    # Define required columns based on correspondence with database keys
    required_columns = ['Handle', 'Title', 'Body (HTML)', 'Image Src', 'SEO Title', 'SEO Description']

    # Check for missing columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Convert DataFrame rows to a list of dictionaries for validation
    data = df[required_columns].to_dict(orient='records')

    # Validate rows using Pydantic
    validated_data = validate_csv_rows(data)
    print(f"Debug: CSV data validated successfully with {len(validated_data)} rows")

    # Return validated data as a DataFrame
    return pd.DataFrame([row.model_dump() for row in validated_data])
