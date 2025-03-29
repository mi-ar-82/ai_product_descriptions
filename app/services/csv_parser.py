import pandas as pd
from app.services.csv_validation import validate_csv_rows

def parse_csv(df:pd.DataFrame) -> pd.DataFrame:
    """
    Parse and validate a CSV file using Pandas and Pydantic.

    Args:
        df (str): Path to the uploaded CSV file.

    Returns:
        pd.DataFrame: DataFrame containing validated data.

    Raises:
        ValueError: If required columns are missing, validation fails, or the file is empty.
    """

    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("The provided CSV file is empty.")

    df = df.fillna('').astype(str)  # Convert all values to strings
    print("Debug: DataFrame converted to strings")
    print(f"Sample data types:\n{df.dtypes.head()}")  # Debug output



    # Define required columns based on correspondence with database keys
    required_columns = ['Handle', 'Title', 'Body (HTML)', 'Image Src', 'SEO Title', 'SEO Description']

    # Check for missing columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Convert DataFrame rows to a list of dictionaries for validation
    data = df[required_columns].astype(str).to_dict(orient='records')  # Force string type
    print("Debug: Converted CSV rows to list, type of data:", type(data))



    # Validate rows using Pydantic
    validated_data = validate_csv_rows(data)
    print(f"Debug: CSV data validated successfully with {len(validated_data)} rows")
    print("Debug: Validated CSV data returned type:", type(validated_data))


    # Return validated data as a DataFrame

    print("------------------------")

    return pd.DataFrame([row.model_dump() for row in validated_data])  # Return validated + cleaned data
