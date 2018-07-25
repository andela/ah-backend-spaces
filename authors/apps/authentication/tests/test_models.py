from django.test import TestCase
from ..models import User, UserManager



class TestUser(TestCase):
    """ Test module for User """

    def setUp(self):
        User.objects.create(
            username="testuser", email="testuser@email.com", is_active=True, is_staff=True)
        User.objects.create(
            username="testuser2", email="testuser2@email.com", is_active=True, is_staff=False)

    def test_string_representation(self):
        user1 = User.objects.get(email="testuser@email.com")
        self.assertEqual(str(user1), "testuser@email.com")

    def test_get_full_name(self):
        """ test get_full_name property"""
        user1 = User.objects.get(email="testuser@email.com")
        user2 = User.objects.get(email="testuser2@email.com")

        self.assertEqual(user1.get_full_name, "testuser")
        self.assertEqual(user2.get_full_name, "testuser2")
        

    def test_get_short_name(self):
        """ test get_shortname property"""
        user1 = User.objects.get(email="testuser@email.com")
        self.assertEqual(user1.get_short_name(), "testuser")


    # def test_create(self):
    #     with mock.patch('django.contrib.auth.models.User') as user_mock:
    #         user_mock.objects = mock.MagicMock()
    #         user_mock.objects.create_user = mock.MagicMock()
    #         user_mock.objects.create_user.return_value = User()

    #         user_manager = UserManager()
    #         user_manager.create_user("gideon", "gideon@email.com")

    #         self.assertTrue(user_mock.objects.create_user.called)



class TestUserManager(TestCase):

    def test_create_user(self):
        """ test module for successfully creating user"""
        created_user = User.objects.create_user(
            username='testhghguser', email='tesuyuyytuser@email.com')
        created_user2 = User.objects.create_user(
            username='gideon', email='gideon@email.com', password='gideon123')


        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        user2 = User.objects.get(email="gideon@email.com")

        self.assertEqual(created_user, user1)
        self.assertEqual(created_user2, user2)
        self.assertEqual(user1.is_staff, False)

    
    def test_create_super_user(self):
        """ test module for successfully creating super user """
        created_user = User.objects.create_superuser(
            username='testhghguser', email='tesuyuyytuser@email.com', password='secret')
        user1 = User.objects.get(email="tesuyuyytuser@email.com")
        self.assertEqual(created_user, user1)

    def test_create_user_without_username(self):
        """ test for typeerror raise if no username is passed"""
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username=None, email="tesuyuyytuser@email.com")

    def test_create_user_without_email(self):
        """ test for typeerror raise if no email is passed"""
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username="testuser", email=None)


    def test_create_super_user_without_password(self):
        """ test for typeerror raise if no password is passed"""
        with self.assertRaises(TypeError):
            User.objects.create_superuser(
                username='testuser', email='tesuyuyytuser@email.com', password=None)

    def test_username_can_exceed_255(self):
        usernames = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien. Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus. Nullam accumsan lorem in dui. Cras ultricies mi eu turpis hendrerit fringilla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; In ac dui quis mi consectetuer lacinia. Nam pretium turpis et arcu. Duis arcu tortor, suscipit eget, imperdiet nec, imperdiet iaculis, ipsum. Sed aliquam ultrices mauris. Integer ante arcu, accumsan a, consectetuer eget, posuere ut, mauris. Praesent adipiscing. Phasellus ullamcorper ipsum rutrum nunc. Nunc nonummy metus. Vestibulum volutpat pretium libero. Cras id dui. Aenean ut"
        user1 = User.objects.create(
            username=usernames, email="testusernames@email.com", is_active=True, is_staff=False)
        user1 = User.objects.get(email="testusernames@email.com")
        self.assertEqual(user1.get_short_name(), usernames)
        