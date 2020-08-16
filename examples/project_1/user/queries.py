from ariadne import QueryType

from ariadne_jwt.decorators import login_required

query = QueryType()


@query.field('me')
@login_required
def resolve_me(obj, info, **kwargs):
    return info.context.get('request').user
