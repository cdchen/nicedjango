# -*- coding: utf-8 -*-

from django.db.models.fields import CharField
from django_extensions.db.fields import UUIDField
import shortuuid


class ShortUUIDField(UUIDField):
    '''
    用來產生適合 HTTP 使用的 UUID 欄位。
    '''

    def pre_save(self, model_instance, add):
        value = CharField.pre_save(self, model_instance, add)
        if self.auto and add and value is None:
            value = shortuuid.encode(self.create_uuid())
            setattr(model_instance, self.attname, value)
        else:
            if self.auto and not value:
                value = shortuuid.encode(self.create_uuid())
                setattr(model_instance, self.attname, value)
        return value

# End of file.
