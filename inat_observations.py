import argparse
import logging
import requests
import time
import urllib.parse

# TODO: move these constants to a common module for sharing
BASE_URL = 'http://api.inaturalist.org/v1/'

ID_PROJECT_HERPS_OF_TX = 411

ID_TAXON_ANURA = 20979

ID_PLACE_BASTROP = 441
ID_PLACE_BLANCO = 1767
ID_PLACE_BURNET = 1909
ID_PLACE_CALDWELL = 1223
ID_PLACE_HAYS = 326
ID_PLACE_TRAVIS = 431
ID_PLACE_WILLIAMSON = 2442

ID_PLACE_CENTRAL_TX = [ID_PLACE_BASTROP, ID_PLACE_BLANCO, ID_PLACE_BURNET,
                       ID_PLACE_CALDWELL, ID_PLACE_HAYS, ID_PLACE_TRAVIS,
                       ID_PLACE_WILLIAMSON]

COUNTY_NAME_MAP = {ID_PLACE_BASTROP: 'Bastrop', ID_PLACE_BLANCO: 'Blanco',
                   ID_PLACE_BURNET: 'Burnet', ID_PLACE_CALDWELL: 'Caldwell',
                   ID_PLACE_HAYS: 'Hays', ID_PLACE_TRAVIS: 'Travis',
                   ID_PLACE_WILLIAMSON: 'Williamson'}

COUNTY_SET = set(ID_PLACE_CENTRAL_TX)

FIELD_CALL_INTENSITY = 980
FIELD_AIR_TEMP_C = 1983
FIELD_AIR_TEMP_F = 5081


def list_to_str(id_list):
    """
    Convert list of IDs (ints) to comma separated string

    :param id_list: list of ints
    :return: list as comma separated string
    """
    string = ''
    for item in id_list:
        string += str(item) + ','
    return string.rstrip(',')


def place_ids_to_county(place_ids, place_guess):
    """
    Convert iNat list of place IDs to a county in Texas

    :param place_ids: list of place IDs
    :param place_guess: the place_guess field from iNat location (as fallback)
    :return: county in Texas matching one of the place IDs
    """
    s = COUNTY_SET.intersection(set(place_ids))
    if len(s) == 1:
        return COUNTY_NAME_MAP[s.pop()]
    else:
        return place_guess


def hot_fields(fields):
    """
    Pull Herps of Texas observation fields for call intensity and air temp
    from 'ofvs' entry in iNat observation

    :param fields: the 'ofvs' entry (list) from an iNat observation
    :return: tuple of call intensity (CI) and air temp (in degrees C)
    """
    call_intensity = ''
    air_temp_c = ''
    for field in fields:
        field_id = field.get('field_id')
        value = field.get('value')
        if value:
            if field_id == FIELD_CALL_INTENSITY:
                # .strip() to convert e.g. "C3" to "3"
                call_intensity = value.strip('\t\n CcIi')
                logging.debug('ci = {}'.format(call_intensity))
            elif field_id == FIELD_AIR_TEMP_C:
                air_temp_c = value
                logging.debug('air_temp_c = {}'.format(air_temp_c))
            elif field_id == FIELD_AIR_TEMP_F:
                air_temp_c = '%.1f' % ((float(value) - 32.0) * 5.0 / 9.0)
                logging.debug('air_temp_c = {} (converted)'.format(air_temp_c))
    return call_intensity, air_temp_c


def query(project_id, quality_grade, taxa, places):
    """
    Call iNat REST interface to query observations matching the provided params

    :param project_id: project ID to match
    :param quality_grade: quality grade to match
    :param taxa: taxa list to match
    :param places: places list to match
    :return: tuples of observation ID, observed date, place,
    species common name, call intensity, air temp (C)
    """
    headers = {'Accept': 'application/json'}
    taxa_str = list_to_str(taxa)
    places_str = list_to_str(places)
    q = 'project_id=' + str(project_id) + '&quality_grade=' + quality_grade \
        + '&taxon_id=' + taxa_str + '&place_id=' + places_str + \
        '&order=desc&order_by=created_at'
    encoded_q = urllib.parse.quote_plus(q, safe=';/?:@&=+$,')
    logging.debug('encoded query = {}'.format(encoded_q))
    url = BASE_URL + 'observations?' + encoded_q
    logging.debug('url = {}'.format(url))

    page = 1
    while True:
        time.sleep(1)  # ensure no more than 60 calls per minute
        r = requests.get(url + '&page=' + str(page), headers=headers)
        logging.debug('r = {}'.format(repr(r)))
        r.raise_for_status()
        data = r.json()
        total_results = data['total_results']
        per_page = data['per_page']
        results = data['results']
        logging.debug('total_results = {}'.format(total_results))
        logging.debug('page = {}'.format(page))
        logging.debug('per_page = {}'.format(per_page))
        logging.debug('len(results) = {}'.format(len(results)))
        for result in data['results']:
            place = place_ids_to_county(result['place_ids'],
                                         result['place_guess'])
            core = (result['id'], result['observed_on'], place,
                    result['taxon']['preferred_common_name'])
            hot = hot_fields(result.get('ofvs'))
            yield core + hot
        logging.debug('page * per_page = {}, total_results = {}'
                      .format(page * per_page, total_results))
        if page * per_page >= total_results:
            break
        page += 1


def main():
    """
    main
    """
    # parse command-line args
    parser = argparse.ArgumentParser(
        description='Query observations from iNaturalist')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable debug logging to STDERR')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug('args = {}'.format(args))

    # set up query params for matching
    # this version gets Herps of Texas frog/toad observations in Central Texas
    project_id = ID_PROJECT_HERPS_OF_TX
    taxa = [ID_TAXON_ANURA]
    places = ID_PLACE_CENTRAL_TX
    # places = [ID_PLACE_TRAVIS]

    # make the query and output the results as CSV
    for result in query(project_id=project_id, quality_grade='research',
                        taxa=taxa, places=places):
        ob_id, date, place, name, ci, temp = result
        print('{},"{}","{}","{}","{}","{}"'
              .format(ob_id, date, place, name, ci, temp))


if __name__ == "__main__":
    main()
