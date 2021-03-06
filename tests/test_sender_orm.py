from django.conf import settings
from django.test import TestCase

from django.contrib.auth import get_user_model

from djwebhooks.decorators import webhook
from djwebhooks.models import WebhookTarget, Delivery

User = get_user_model()
WEBHOOK_EVENTS = getattr(settings, "WEBHOOK_EVENTS", None)


class BasicTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )

        self.identifier1 = 'afdasfjasd3485'
        self.identifier2 = 'vrefr9jqaw9efj'

        self.webook_target = WebhookTarget.objects.create(
            owner=self.user,
            event=WEBHOOK_EVENTS[0],
            identifier=self.identifier1,
            target_url="http://httpbin.org/post"
        )
        self.fail_target = WebhookTarget.objects.create(
            owner=self.user,
            event=WEBHOOK_EVENTS[1],
            identifier=self.identifier2,
            target_url="http://httpbin.org/status/400"
        )

    def test_webhook(self):

        @webhook(event=WEBHOOK_EVENTS[0])
        def basic(owner, identifier):
            return {"what": "me worry?"}

        results = basic(owner=self.user, identifier=self.identifier1)

        self.assertEqual(results['what'], "me worry?")

        self.assertEqual(Delivery.objects.count(), 1)

        d = Delivery.objects.latest()

        self.assertEqual(d.success, True)

    def test_failed_webhook(self):

        @webhook(event=WEBHOOK_EVENTS[1])
        def basic(owner, identifier):
            return {"what": "me worry?"}

        results = basic(owner=self.user, identifier=self.identifier2)

        self.assertEqual(results['what'], "me worry?")

        d = Delivery.objects.latest()

        self.assertEqual(d.success, False)

    def test_event_dkwarg(self):

        @webhook(number=123)
        def basic(owner, identifier):
            return {"what": "me worry?"}

        self.assertRaises(TypeError, basic, self.user)

    def test_owner_kwarg(self):

        @webhook(event=WEBHOOK_EVENTS[0])
        def basic():
            return {"what": "me worry?"}

        self.assertRaises(TypeError, basic)

    def test_identifier_kwarg(self):

        @webhook(event=WEBHOOK_EVENTS[0])
        def basic(owner='pydanny'):
            return {"what": "me worry?"}

        with self.assertRaises(TypeError):
            basic(owner='danny')

    def test_cant_find_webhook_target(self):
        # TODO
        pass
