class ValidationUtils:
    """
    Clase estática para validar diccionarios de configuración
    en estructuras de generación de datos.
    """

    @staticmethod
    def validate_config_dict(config_dict: dict) -> bool:
        """
        Valida que el diccionario de configuración tenga la estructura
        requerida para cada tipo de dato (string, int, float, boolean, date).
        """
        columns = config_dict.get('columns', {})
        if not columns:
            return False

        for _, props in columns.items():
            col_type = props.get('type')

            if col_type == 'string':
                # Debe tener una lista 'values' no vacía
                if not props.get('values'):
                    return False

            elif col_type == 'int':
                # Debe tener 'min' y 'max'
                if 'min' not in props or 'max' not in props:
                    return False

            elif col_type == 'float':
                # Debe tener 'min' y 'max'
                if 'min' not in props or 'max' not in props:
                    return False

            elif col_type == 'date':
                # Debe tener 'start' y 'end'
                if 'start' not in props or 'end' not in props:
                    return False

            elif col_type == 'boolean':
                # No requiere más validaciones
                continue

            else:
                # Tipo desconocido
                return False

        return True
