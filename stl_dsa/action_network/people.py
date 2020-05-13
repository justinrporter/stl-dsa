import json
import requests
from django.conf import settings

from stl_dsa.action_network import exception


def add_person(user, tags=[]):
    """Add a user to ActionNetwork's db via a POST.
    """
    payload = {
        "person": {
            "family_name": user.last_name,
            "given_name": user.first_name,
        },
        "add_tags": tags
    }

    r = requests.post(
        '%s/api/v2/people/' % settings.ACTIONNETWORK_ROOT,
        headers={'OSDI-API-Token': settings.ACTIONNETWORK_API_KEYS[0]},
        data=payload
    )

    assert r.status_code == 200

    identifiers = [i.split(':') for i in json.loads(r.content)['identifiers']]
    for identifier_type, identifier in identifiers:
        if identifier_type == 'action_network':
            return identifier

    # if we got here, we didn't get an AN UUID in the response
    raise exception.ActionNetworkException()


def update_person_email(actn_uuid, from_address, to_address):
    """Add update a user's email with a PUT.
    """

    # get the current state of the user from actionnetwork
    r = requests.get(
        '%s/api/v2/people/%s' % (settings.ACTIONNETWORK_ROOT, actn_uuid),
        headers={'OSDI-API-Token': settings.ACTIONNETWORK_API_KEYS[0]},
    )
    addresses = json.loads(r.content)['email_addresses']

    # iterate through email addresses, if the old one is in there,
    # replace it and note you've done it.
    overwrite = False
    for email_dict in addresses:
        if email_dict['address'] == from_address:
            email_dict['address'] = to_address
            overwrite = True

    # if it wasn't overwritten, append the new email to the list and
    # make it primary and subscribed.
    if not overwrite:
        for email_dict in addresses:
            if email_dict['primary']:
                email_dict['primary'] = False

        addresses.append({
            "primary": True,
            "address": to_address,
            "status": "subscribed"
        })

    requests.put(
        '%s/api/v2/people/%s' % (settings.ACTIONNETWORK_ROOT, actn_uuid),
        headers={'OSDI-API-Token': settings.ACTIONNETWORK_API_KEYS[0]},
        data=addresses
    )

    # TODO? not sure what this function should return, other than
    # exception if doesn't work.
