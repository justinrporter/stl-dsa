import json
import datetime
from unittest import mock

from django.utils.timezone import now
from django.conf import settings


NEW_USER_UUID = 'd32fcdd6-7366-466d-a3b8-7e0d87c3cd8b'


def generate_user_json(uuid, given_name, family_name, email_addresses=[],
                       postal_addresses=[], identifiers=[], languages=['en']):

    if postal_addresses:
        assert postal_addresses == postal_addresses[0]['postal_code'] == 20009

    d = {
        "identifiers": [
            "action_network:%s" % uuid,
        ] + identifiers,
        "created_date": now(),
        "modified_date": now(),
        "family_name": family_name,
        "given_name": given_name,
        "email_addresses": [
            {
                # true for only the first address passed through;
                # no idea if this is what action network actually does.
                "primary": i == 0,
                "address": addr,
                "status": "subscribed"
            } for i, addr in enumerate(email_addresses)
        ],
        "postal_addresses": [
            {
                "primary": i == 0,
                "address_lines": [
                    "1900 Pennsylvania Ave"
                ],
                "locality": "Washington",
                "region": "DC",
                "postal_code": "20009",
                "country": "US",
                "language": "en",
                "location": {
                    "latitude": 38.919,
                    "longitude": -77.0379,
                    "accuracy": "Approximate"
                }
            } for i, addrspec in enumerate(postal_addresses)
        ],
        "languages_spoken": languages,
        "_links": {
            "self": {
                "href": "%s/api/v2/people/%s" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:attendances": {
                "href": "%s/api/v2/people/%s/attendances" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:signatures": {
                "href": "%s/api/v2/people/%s/signatures" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:submissions": {
                "href": "%s/api/v2/people/%s/submissions" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:donations": {
                "href": "%s/api/v2/people/%s/donations" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:outreaches": {
                "href": "%s/api/v2/people/%s/outreaches" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "osdi:taggings": {
                "href": "%s/api/v2/people/%s/taggings" %
                (settings.ACTIONNETWORK_ROOT, uuid)
            },
            "curies": [
                {
                    "name": "osdi",
                    "href": "%s/docs/v2/{rel}" %
                            settings.ACTIONNETWORK_ROOT,
                    "templated": True
                }, {
                    "name": "action_network",
                    "href": "%s/docs/v2/{rel}" %
                            settings.ACTIONNETWORK_ROOT,
                    "templated": True
                }
            ]
        }
    }

    return d


def json_datetime(obj):
    """Format an object as a JSON timestamp (if it's a datetime)
    """
    return (
        obj.isoformat()
        if isinstance(obj, (datetime.datetime, datetime.date))
        else None
    )


def mock_post(url, headers, data):

    assert url.find('https://fake-an.com') == 0

    assert len(headers) == 1
    assert headers['OSDI-API-Token'] == settings.ACTIONNETWORK_API_KEYS[0]

    return mock.Mock(
        status_code=200,
        content=fake_created_user_create_response_content(data)
    )


def fake_created_user_create_response_content(payload):
    """Respond to a payload by generating a fake response.

    Based on the documentation here:
    https://actionnetwork.org/docs/v2/post-people/

    """

    # Example Payload:
    # {
    #   "person" : {
    #     "identifiers": [
    #       "my_system:1"
    #     ],
    #     "family_name" : "Smith",
    #     "given_name" : "John",
    #     "postal_addresses" : [ { "postal_code" : "20009" }],
    #     "email_addresses" : [ { "address" : "jsmith@mail.com" }]
    #   },
    #   "add_tags": [
    #     "volunteer",
    #     "member"
    #   ]
    # }

    given_name = payload["person"]['given_name']
    family_name = payload["person"]['family_name']
    identifiers = payload["person"].get('identifiers', [])
    email_addresses = [a["address"] for a in
                       payload["person"].get("email_addresses", [])]
    postal_addresses = [a["address"] for a in
                        payload["person"].get("postal_addresses", [])]

    response_dict = generate_user_json(
        uuid=NEW_USER_UUID,
        given_name=given_name,
        family_name=family_name,
        identifiers=identifiers,
        email_addresses=email_addresses,
        postal_addresses=postal_addresses
    )

    return json.dumps(response_dict, default=json_datetime)
