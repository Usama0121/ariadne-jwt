from ariadne import load_schema_from_path
from django.contrib.auth import get_user_model
from ariadne import make_executable_schema, QueryType, MutationType

from ariadne_jwt import verify, refresh, genericScalar
import ariadne_jwt

type_defs = load_schema_from_path('./')
type_defs += ariadne_jwt.mutations.jwt_schema
query = QueryType()
mutation = MutationType()


@query.field('user')
def resolve_user(obj, info, **kwargs):
    return get_user_model().objects.all()


mutation.set_field('verifyToken', verify)
mutation.set_field('refreshToken', refresh)

schema = make_executable_schema(type_defs, [query, mutation, genericScalar])
