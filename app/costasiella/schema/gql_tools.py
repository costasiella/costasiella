# To convert relay node id to real id
from collections import namedtuple
from graphql_relay.node.node import from_global_id

def get_rid(global_id):
    Rid = namedtuple('Rid', 'name id')
    return Rid(*from_global_id(global_id))