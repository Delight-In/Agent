import pandas as pd

REQUIRED_COLUMNS = ['Name', 'Phone', 'Email']


def parse_excel(file_storage):
    """
    Parses an uploaded Excel file from Flask's FileStorage object.
    Returns a tuple: (list of contact dicts, message)
    """
    try:
        # Read Excel file into a DataFrame
        df = pd.read_excel(file_storage)
    except Exception as e:
        return None, f"❌ Error reading Excel file: {str(e)}"

    # Ensure required columns are present
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        return None, f"❌ Missing required columns: {', '.join(missing_columns)}"

    contacts = []

    # Iterate over rows and extract valid contacts
    for idx, row in df.iterrows():
        name = str(row.get('Name', '')).strip()
        phone = str(row.get('Phone', '')).strip()
        email = str(row.get('Email', '')).strip()

        if not name or not phone or not email:
            print(f"⚠️ Row {idx + 2} skipped — missing fields: Name='{name}', Phone='{phone}', Email='{email}'")
            continue

        contacts.append({
            'name': name,
            'phone': phone,
            'email': email
        })

    if not contacts:
        return None, "❌ No valid contacts found in the Excel file."

    return contacts, f"✅ Successfully parsed {len(contacts)} contact(s)."
