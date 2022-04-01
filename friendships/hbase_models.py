from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    from_user_id = models.IntegerField(reverse=True)
    to_user_id = models.IntegerField(column_family='following')
    created_at = models.TimestampField()

    class Meta:
        table_name = 'friendship_followings'
        row_key = ('from_user_id', 'created_at')

    def __str__(self):
        encoding = f'following: ' \
                   f'{self.from_user_id}:' \
                   f'{self.created_at} - ' \
                   f'{self.to_user_id}'
        return encoding


class HBaseFollower(models.HBaseModel):
    to_user_id = models.IntegerField(reverse=True)
    from_user_id = models.IntegerField(column_family='follower')
    created_at = models.TimestampField()

    class Meta:
        table_name = 'friendship_followers'
        row_key = ('to_user_id', 'created_at')

    def __str__(self):
        encoding = f'follower: ' \
                   f'{self.to_user_id}:' \
                   f'{self.created_at} - ' \
                   f'{self.from_user_id}'
        return encoding
