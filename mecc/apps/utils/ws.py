from django.conf import settings

from britney.middleware import auth, format
from britney.errors import SporeMethodCallError, SporeMethodStatusError

import britney_utils
import urllib
import json

from django.utils.translation import ugettext as _
from datetime import date, datetime


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
                        "first_name": i['first_name'].title(),
                        "status": employee_type,
                        "cmp": cmp,
                        "birth_date": i['birth_date'],
                        "id_member": e['username'],
                        "mail": e['mail'],
                    }
                    if person not in result and '@etu.unistra.fr' \
                       not in person['mail'] and person[("status")] == employee_type:
                        result.append(person)

    if r['next'] != None:
        page_num += 1
        get_list_from_cmp(cmp, employee_type, page_num=page_num, result=result)

    return result


def get_from_ldap(val):

    def process_stuff(ask):
        result = []
        r = json.loads(ask.text)
        for e in r:
            if e['is_active']:
                if e['primary_affiliation'] == 'student':
                    affiliation = _('Étudiant')
                    cmp = e['main_registration_code'] if e['main_registration_code'] != None else _('Non renseigné')
                else:
                    cmp = e['main_affectation_code'] if e['main_affectation_code'] != None else _('Non renseigné')
                    if e['primary_affiliation'] == 'employee':
                        affiliation = _('Administratif')
                    else:
                        affiliation = _('Enseignant')
                    person = {
                        "last_name": e['last_name'],
                        "first_name": e['first_name'].title(),
                        "status": affiliation,
                        "institute": cmp,
                        "birth_date": e['birth_date'],
                        "username": e['username'],
                        "mail": e['mail'],
                        }
                    result.append(person)
        return result

    client = create_client('ldap_client', settings.LDAP_TOKEN,
                           settings.LDAP_SPORE, settings.LDAP_BASE_URL)

    ask = client.list_accounts(
        format='json', establishment='UDS', last_or_birth_name=val
    )

    return process_stuff(ask)

def get_pple(val):

    last_year = date.today().year - 1
    current_date = datetime.now()
    client = create_client('camelot_client', settings.CAMELOT_TOKEN,
                           settings.CAMELOT_SPORE, settings.CAMELOT_BASE_URL)

    goto = [
        client.get_persons(format='json', username=val),
        client.get_persons(format='json', last_name=val),
        client.get_persons(format='json', birth_name=val)
    ]

    result = []

    for e in goto:
        r = json.loads(e.text)
        if r and 'results' in r and r['results']:
            for i in r['results']:
                for e in i['accounts']:
                    if e['is_active'] == True:
                        person = {
                            "last_name": i['last_name'],
                            "birth_name": i['birth_name'],
                            "first_name": i['first_name'].title(),
                            "birth_date": i['birth_date'],
                        }
                        for student in i['student_states']:
                            if int(student['registration_year']) >= last_year and student['comp'] != "DES":
                                extra = {
                                    "institute": student['comp'],
                                    "status": "STU",
                                    "mail": e['mail'],
                                    "username": e['username']
                                }
                                person.update(extra)
                                if person not in result:
                                    result.append(person)

                        for employee in i['employee_states']:
                            if employee['end_date'] is None or datetime.strptime(employee['end_date'], "%Y-%m-%d") >= current_date:
                                extra = {
                                    "institute": employee['affiliation'],
                                    "status": 'ADM' if employee['type'] == 'Administratif' else 'PROF',
                                    "mail": e['mail'],
                                    "username": e['username']
                                }
                                person.update(extra)
                                if person not in result:
                                    result.append(person)
    return result


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
