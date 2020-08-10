from ariadne import QueryType
from django.contrib.auth import get_user_model

from ariadne_jwt.decorators import login_required

query = QueryType()


@query.field('me')
@login_required
def resolve_me(obj, info, **kwargs):
    return info.context.get('request').user
