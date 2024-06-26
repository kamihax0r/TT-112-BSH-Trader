import customer_info

def test_connection():
    result = customer_info.get_customer_info()
    if 'error' in result:
        return {"error": result['error']}
    
    # Extracting and formatting the information
    first_name = result.get('first_name')
    last_name = result.get('last_name')
    email = result.get('email')
    address = result.get('address')
    phone = result.get('mobile_phone_number')
    birth_date = result.get('birth_date')
    permitted_account_types = result.get('permitted_account_types')
    
    welcome_message = f"""
    Welcome, {first_name} {last_name}!
    
    Here is your information:
    Email: {email}
    Phone: {phone}
    Birth Date: {birth_date}
    
    Address:
        {address.get('street-one')}
        {address.get('city')}, {address.get('state-region')} {address.get('postal-code')}
        {address.get('country')}
    
    Permitted Account Types:
    """
    
    for account in permitted_account_types:
        welcome_message += f"""
    Account Type: {account.get('name')}
    Publicly Available: {account.get('is_publicly_available')}
    Tax Advantaged: {account.get('is_tax_advantaged')}
    Has Multiple Owners: {account.get('has_multiple_owners')}
    Margin Types:
"""
        for margin in account.get('margin_types'):
            welcome_message += f"        - {margin.get('name')} (Margin: {margin.get('is_margin')})\n"
    
    return {"message": welcome_message}
