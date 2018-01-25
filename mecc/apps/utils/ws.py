"""
Webservices stuff here
"""
import json
import urllib
import britney_utils

from britney.middleware import auth, format
from britney.errors import SporeMethodCallError, SporeMethodStatusError
from django.conf import settings
from django.utils.translation import ugettext as _

TEACHER_GRADES = [
    "ENSEIGNANT",
    "MAITRE",
    "MCUPH",
    "PROF",
    "PUPH",
]


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
        raise Exception("Spore returns error : %s" % e)
    except urllib.error.URLError as e:
        raise Exception("Wrong url for spore")
    return client


def get_list_from_cmp_by_ldap(cmp):
    """
    Return list of selected employee_type from a selected affectation
    """
    employee_type = {'faculty': 'Enseignant', 'employee': 'Administratif'}
    client = create_client(
        'ldap_client', settings.LDAP_TOKEN, settings.LDAP_SPORE,
        settings.LDAP_BASE_URL
    )
    ask = client.list_users(format='json', affectation=cmp)
    r = json.loads(ask.text)
    result = []
    for e in r:
        if e.get('is_active'):
            person = {
                "last_name": e['last_name'],
                "birth_name": e['birth_name'],
                "first_name": e['first_name'].title(),
                "status": employee_type.get(e.get('primary_affiliation')),
                "cmp": cmp,
                "birth_date": e['birth_date'],
                "id_member": e['username'],
                "mail": e['mail'],
            }
            if person not in result:
                result.append(person)

    return result


def get_user_from_ldap(username):
    """
    return data from user
    """
    client = create_client('ldap_client', settings.LDAP_TOKEN,
                           settings.LDAP_SPORE, settings.LDAP_BASE_URL)
    ask = client.get_user(format='json', username=username)
    return json.loads(ask.text)


def get_from_ldap(val):
    """
    return list of user with data from ldap
    """
    def process_stuff(ask):
        result = []
        r = json.loads(ask.text)
        for e in r:
            if e['is_active']:
                if e['primary_affiliation'] == 'student':
                    affiliation = _('Étudiant')
                    cmp = e['main_registration_code'] if e[
                        'main_registration_code'] is not None else _(
                            'Non renseigné')
                else:
                    cmp = e['main_affectation_code'] if e[
                        'main_affectation_code'] is not None else _(
                            'Non renseigné')
                    if e['primary_affiliation'] == 'employee':
                        affiliation = _('Administratif')
                    else:
                        affiliation = _('Enseignant')
                person = {
                    "last_name": "%s (%s)" % (e['last_name'], val.capitalize(
                        )) if val.capitalize() != e['last_name'].capitalize(
                            ) and '*' not in val else e['last_name'],
                    "first_name": e.get('first_name').title(),
                    "status": affiliation,
                    "institute": cmp,
                    "birth_date": e.get('birth_date'),
                    "username": e.get('username'),
                    "mail": e.get('mail'),
                    "birth_name": e.get('birth_name').title()
                    }
                result.append(person)
        return result
    client = create_client('ldap_client', settings.LDAP_TOKEN,
                           settings.LDAP_SPORE, settings.LDAP_BASE_URL)
    ask = client.list_accounts(
        format='json', establishment='UDS', last_or_birth_name=val)

    return process_stuff(ask)


def ask_camelot(val):
    client = create_client('camelot_client', settings.CAMELOT_TOKEN,
                           settings.CAMELOT_SPORE, settings.CAMELOT_BASE_URL)
    goto = [
        client.get_persons(format='json', username=val),
        client.get_persons(format='json', last_name=val),
        client.get_persons(format='json', birth_name=val)
        # client.get_persons(format='json', first_name=val)
    ]
    result = []
    for e in goto:
        r = json.loads(e.text)
        if r and 'results' in r and r['results']:
            for i in r['results']:
                a = {
                    "first_name": i['first_name'].title(),
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
