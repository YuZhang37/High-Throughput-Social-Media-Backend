
class HBaseField:
    data_type = None

    def __init__(self,
                 reverse=False,
                 column_family=None,
                 is_required=True,
                 default=None,
                 *args,
                 **kwargs):
        self.reverse = reverse
        self.column_family = column_family
        self.is_required = is_required
        self.default = default


class IntegerField(HBaseField):
    data_type = 'int'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimestampField(HBaseField):
    data_type = 'timestamp'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

