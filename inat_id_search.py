import argparse
import logging
import requests
import urllib.parse

# TODO: move these constants to a common module for sharing
BASE_URL = 'http://api.inaturalist.org/v1/'

OP_PLACES = 'places/autocomplete'
OP_PROJECTS = 'projects'
OP_TAXA = 'taxa'
OP_USERS = 'users/autocomplete'

MAP_OP_TO_NAME_KEY = {OP_PLACES: 'display_name',
                      OP_PROJECTS: 'title',
                      OP_TAXA: 'name',
                      OP_USERS: 'name'}


def query(op, q):
    """
    Call iNat REST interface to lookup the ID of places, projects, taxa or
    users matching the `q` param

    :param op: REST operation for the type of query (e.g. 'projects')
    :param q: start of the name of the resource to query (e.g. 'Herps of Tex')
    :return: tuples of resource ID, name of resource
    """
    headers = {'Accept': 'application/json'}
    encoded_q = urllib.parse.quote_plus(q)
    url = BASE_URL + op + '?q=' + encoded_q
    logging.debug('url = {}'.format(url))

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    logging.debug('r = {}'.format(repr(r)))
    # logging.debug('response data = {}'.format(data))
    logging.debug('{} {} found with name starting with "{}"'
                  .format(data['total_results'], op.split('/')[0], q))
    logging.debug('{} results per page'.format(data['per_page']))

    # TODO: fetch additional pages if needed (use a max limit?)
    for result in data['results']:
        yield result['id'], result[MAP_OP_TO_NAME_KEY[op]]


def main():
    """
    main
    """
    # parse command-line args
    parser = argparse.ArgumentParser(
        description='Lookup IDs on iNaturalist')
    parser.add_argument('name', type=str,
                        help='the name of the iNaturalist resource to lookup')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--location', action='store_true',
                       help='search for a location (place) ID')
    group.add_argument('-p', '--project', action='store_true',
                       help='search for a project ID')
    group.add_argument('-t', '--taxon', action='store_true',
                       help='search for a taxon ID')
    group.add_argument('-u', '--user', action='store_true',
                       help='search for a user ID')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable debug logging to STDERR')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.location:
        op = OP_PLACES
    elif args.project:
        op = OP_PROJECTS
    elif args.taxon:
        op = OP_TAXA
    else:
        op = OP_USERS

    logging.debug('args = {}'.format(args))
    logging.debug('name = {}'.format(args.name))

    # query the IDs and print the results
    for identifier, name in query(op=op, q=args.name):
        print('id={}, name="{}"'.format(identifier, name))


if __name__ == "__main__":
    main()
