
def str2(s: str, TypeTransforms={None: lambda:'', }, ValueTransforms={None: lambda:''}) -> str:
    """
    Convert input to string, handling "special values or types".
    :param s: Input value.
    :param TypeTransforms: Dict mapping types to functions that return strings.
    :param ValueTransforms: Dict mapping specific values to functions that return strings.
    :return: String representation of input.
    
    By default, None is converted to an empty string.
    """
    if s in ValueTransforms:
        return ValueTransforms[s]()
    if s in TypeTransforms:
        return TypeTransforms[s]()
    return str(s)