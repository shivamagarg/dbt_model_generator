import re

def extract_table_name(ddl_path):
    """Extract table name from DDL file"""
    with open(ddl_path, 'r') as f:
        ddl_content = f.read()
    
    table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\"?(\w+)\"?\.)?"?(\w+)"?'
    match = re.search(table_pattern, ddl_content, re.IGNORECASE)
    
    if match:
        schema = match.group(1) or ''
        table = match.group(2)
        return f"{schema}.{table}".upper() if schema else table.upper()
    
    return "Unknown_Table"

def parse_ddl_file(ddl_path):
    """Parse DDL file to extract column information and constraints"""
    with open(ddl_path, 'r') as f:
        ddl_content = f.read()
    
    # Extract column definitions
    column_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(?:\w+)\s*\((.*?)\)[^)]*$'
    match = re.search(column_pattern, ddl_content, re.IGNORECASE | re.DOTALL)
    
    if not match:
        raise ValueError("Could not find column definitions in DDL file")
        
    columns_text = match.group(1)
    columns = []
    unique_keys = []
    
    for line in columns_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        # Check for UNIQUE KEY constraint
        if 'UNIQUE' in line.upper() and 'KEY' in line.upper():
            uk_pattern = r'\((.*?)\)'
            uk_match = re.search(uk_pattern, line)
            if uk_match:
                uk_cols = [col.strip().strip('"') for col in uk_match.group(1).split(',')]
                unique_keys.extend(uk_cols)
            continue
            
        parts = line.split(None, 2)
        if len(parts) >= 2:
            column_name = parts[0].strip('"')
            column_type = parts[1]
            columns.append((column_name, column_type))
    
    return columns, unique_keys