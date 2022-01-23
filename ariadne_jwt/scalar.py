from ariadne.scalars import ScalarType
from graphql import (StringValueNode, BooleanValueNode, IntValueNode,
                     FloatValueNode, ListValueNode, ObjectValueNode)

try:
    from graphql.type.scalars import (MAX_INT as GRAPHQL_MAX_INT,
                                      MIN_INT as GRAPHQL_MIN_INT)
except ImportError:
    from graphql.type.scalars import GRAPHQL_MAX_INT, GRAPHQL_MIN_INT

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
        if GRAPHQL_MAX_INT <= num <= GRAPHQL_MIN_INT:
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
