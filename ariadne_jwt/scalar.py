from ariadne.scalars import ScalarType
from graphql.type.scalars import MAX_INT, MIN_INT
from graphql import StringValueNode, BooleanValueNode, IntValueNode, FloatValueNode, ListValueNode, ObjectValueNode

GenericScalar = ScalarType('GenericScalar')


@GenericScalar.serializer
@GenericScalar.value_parser
def identity(value):
    return value


@GenericScalar.literal_parser
def parse_literal(ast):
    if isinstance(ast, (StringValueNode, BooleanValueNode)):
        return ast.value
    elif isinstance(ast, IntValueNode):
        num = int(ast.value)
        if MIN_INT <= num <= MAX_INT:
            return num
    elif isinstance(ast, FloatValueNode):
        return float(ast.value)
    elif isinstance(ast, ListValueNode):
        return [parse_literal(value) for value in ast.values]
    elif isinstance(ast, ObjectValueNode):
        return {
            field.name.value: parse_literal(field.value)
            for field in ast.fields
        }
    else:
        return None
