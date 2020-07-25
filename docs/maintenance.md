# Clear expired tokens

Delete revoked refresh tokens with `cleartokens` command.

$ python manage.py cleartokens --help
usage: cleartokens [--expired]
optional arguments:
  --expired             Clears expired tokens

The `--expired` argument allows the user to remove those refresh tokens whose lifetime is greater than the amount specified by `JWT_REFRESH_EXPIRATION_DELTA` setting.

source: [Refresh token &#8212; Django GraphQL JWT 0.3.1 documentation](https://django-graphql-jwt.domake.io/en/stable/refresh_token.html)


