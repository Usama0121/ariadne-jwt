from ariadne import make_executable_schema, load_schema_from_path
from django.conf import settings

from user.mutations import mutation
from user.queries import query
from ariadne_jwt import jwt_schema, GenericScalar
import os

root_type_defs = load_schema_from_path(os.path.join(settings.BASE_DIR, 'project_1'))
user_type_defs = load_schema_from_path(os.path.join(settings.BASE_DIR, 'user'))

schema = make_executable_schema([root_type_defs, user_type_defs, jwt_schema], [query, mutation, GenericScalar])
