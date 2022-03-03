from core.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def setUp(self) -> None:
        self.clear_cache()

    def test_profile_property(self):
        user1 = self.create_user('user1')
        self.assertEqual(UserProfile.objects.count(), 0)
        profile, created = user1.get_or_create_userprofile()
        self.assertEqual(created, True)
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)

        user2 = self.create_user('user2')
        self.assertEqual(UserProfile.objects.count(), 1)
        profile = user2.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 2)
