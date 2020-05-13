from django.dispatch import receiver

from allauth.account import signals as allauth_signals

from stl_dsa.action_network import people


@receiver(allauth_signals.user_signed_up)
def register_user_with_actionnetwork(request, user):

    user.actn_uuid = people.add_person(user, tags=['website-member'])
    user.save()


@receiver(allauth_signals.email_changed)
def update_user_email(
        request, user, from_email_address, to_email_address):

    people.update_person_email(
        user=user,
        from_address=from_email_address,
        to_address=to_email_address)
