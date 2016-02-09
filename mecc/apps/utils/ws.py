from django.conf import settings

from britney.middleware import auth, format
from britney.errors import SporeMethodCallError, SporeMethodStatusError

import britney_utils
import urllib
import json

from django.utils.translation import ugettext_lazy as _


def create_client(name, token, spore, base_url):
    """
    Return SPORE client
    """

    middlewares = (
        (format.Json,),
        (auth.ApiKey, {'key_name': 'Authorization',
         'key_value': 'Token %s' % token})
    )
    try:
        client = britney_utils.get_client(name, spore, base_url,
                                          middlewares=middlewares)

    except (SporeMethodStatusError, SporeMethodCallError) as e:
        raise InvalidParamError("Spore returns a %s" % e)
    except urllib.error.URLError as e:
        raise Exception("Wrong url for spore")
    return client


def get_list_from_cmp(cmp, employee_type, page_num=1, result=[]):

    if employee_type not in['Enseignant', 'Administratif']:
        raise Exception(_('Mauvais type pour get_list_from_cmp'))
    client = create_client(
        'camelot_client', settings.CAMELOT_TOKEN, settings.CAMELOT_SPORE,
        settings.CAMELOT_BASE_URL
    )
    ask = client.get_persons(
        format='json', employee_type=employee_type, structure=cmp,
        page_size=500, page=page_num
    )
    r = json.loads(ask.text)

# FIXME: content belows work but can be improved perhaps with list comprehension
    if r and 'results' in r and r['results']:
        for i in r['results']:
            for e in i['accounts']:
                if e['is_active'] == True:
                    person = {
                        "last_name": i['last_name'],
                        "birth_name": i['birth_name'],
                        "first_name": i['first_name'],
                        "status": employee_type,
                        "cmp": cmp,
                        "birth_date": i['birth_date'],
                        "id_member": e['username'],
                        "mail": e['mail'],
                    }
                    if person not in result and '@etu.unistra.fr' not in person['mail']:
                        result.append(person)

    if r['next'] != None:
        page_num += 1
        get_list_from_cmp(cmp, employee_type, page_num=page_num, result=result)

    return result


def ask_camelot(val):
    # Getting key and value from first elements of first dict
    # k = next(iter(args[0].keys()))
    # v = next(iter(args[0].values()))

    client = create_client('camelot_client', settings.CAMELOT_TOKEN,
                           settings.CAMELOT_SPORE, settings.CAMELOT_BASE_URL)

    goto = [
        client.get_persons(format='json', username=val),
        client.get_persons(format='json', last_name=val),
        client.get_persons(format='json', birth_name=val)
        # client.get_persons(format='json', first_name=val)
    ]

    result = []
    vart = 0
    for e in goto:
        r = json.loads(e.text)
        vart += 1
        vart += 1
        if r and 'results' in r and r['results']:
            for i in r['results']:

                a = {
                    "first_name": i['first_name'],
                    "last_name": i['last_name'],
                }
                mails = []

                if i['accounts']:
                    for m in i['accounts']:
                        a.update({"id_member": m['username']})
                        mails.append(m['mail'])
                a.update({"mail": mails})

                if a not in result:
                    result.append(a)

    return result
