from ariadne import QueryType, make_executable_schema, load_schema_from_path
from django.conf import settings

from user.mutations import mutation
from ariadne_jwt import jwt_schema, GenericScalar
import os

mutation_type = load_schema_from_path(os.path.join(settings.BASE_DIR, 'project_1'))
user_schema = load_schema_from_path(os.path.join(settings.BASE_DIR, 'user'))
type_defs = """
    type Query {
        hello: String!
    }
"""

query = QueryType()


@query.field("hello")
def resolve_hello(*_):
    return "Hello world!"


schema = make_executable_schema([type_defs, jwt_schema, mutation_type, user_schema], [query, mutation, GenericScalar])
