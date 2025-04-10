def validate_config_dict(config_dict: dict) -> bool:
    """
    Validate that the configuration dictionary has the required structure
    for each data type (string, int, float, boolean, date).
    """
    columns = config_dict.get('columns', {})
    if not columns:
        return False

    for _, properties in columns.items():
        col_type = properties.get('type')

        if col_type == 'string':
            # Must have a non-empty 'values' list
            if not properties.get('values'):
                return False

        elif col_type == 'int':
            # Must have 'min' and 'max'
            if 'min' not in properties or 'max' not in properties:
                return False

        elif col_type == 'float':
            # Must have 'min' and 'max'
            if 'min' not in properties or 'max' not in properties:
                return False

        elif col_type == 'date':
            # Must have 'start' and 'end'
            if 'start' not in properties or 'end' not in properties:
                return False

        elif col_type == 'boolean':
            # boolean has no additional constraints
            continue

        else:
            # Unknown type
            return False

    return True
