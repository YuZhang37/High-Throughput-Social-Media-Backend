

def user_changed(sender, instance, **kwargs):
    from core.services import UserService
    # print("invalidate: ", instance.id, instance.username)
    UserService.invalidate_user(instance.id)


def user_profile_changed(sender, instance, **kwargs):
    from core.services import UserService
    UserService.invalidate_user_profile(instance.user_id)
