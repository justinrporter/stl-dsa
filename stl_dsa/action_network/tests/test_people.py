import uuid
import json
from unittest import mock

from django.test import override_settings

from stl_dsa.action_network import people
from stl_dsa.action_network.tests import factories


@override_settings(ACTIONNETWORK_ROOT='https://fake-an.com')
@override_settings(ACTIONNETWORK_API_KEYS=['deadbeef'])
def test_update_user():

    u = mock.Mock(
        first_name='FirstName',
        last_name='LastName',
        email='initial@gmail.com',
        actn_uuid=uuid.uuid4()
    )

    def mock_get(url, headers):
        assert url.find('https://fake-an.com') == 0

        d = factories.generate_user_json(
            uuid=u.uuid,
            given_name=u.first_name,
            family_name=u.last_name,
            email_addresses=[u.email],
        )

        return mock.Mock(
            content=json.dumps(d, default=factories.json_datetime),
            status_code=200
        )

    def mock_put(url, headers, data):
        assert url == 'https://fake-an.com/api/v2/people/%s' % u.actn_uuid

        assert data == [{'primary': True,
                         'address': 'new_email@gmail.com',
                         'status': 'subscribed'}]

    with mock.patch('requests.get', mock_get):
        with mock.patch('requests.put', mock_put):
            people.update_person_email(
                u.actn_uuid, u.email, 'new_email@gmail.com')


@override_settings(ACTIONNETWORK_ROOT='https://fake-an.com')
@override_settings(ACTIONNETWORK_API_KEYS=['deadbeef'])
def test_add_user():

    user = mock.Mock(
        first_name='FirstName',
        last_name='LastName',
    )

    def mock_post(url, headers, data):
        assert url == 'https://fake-an.com/api/v2/people/'

        assert data['person']['family_name'] == user.last_name
        assert data['person']['given_name'] == user.first_name
        assert data["add_tags"] == []

        return factories.mock_post(url, headers, data)

    with mock.patch('requests.post', mock_post):
        an_uuid = people.add_person(user)

    assert an_uuid == factories.NEW_USER_UUID
