# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models.fields import CharField, NOT_PROVIDED
from django.utils.functional import curry
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


class HandlerField(CharField):
    '''
    儲存 Handler 資訊的欄位。

    用法範例：

    >>> class MyModel(models.Model):
    >>>    handler = HandlerField(factory_cls=HandlerFactory)
    >>>

    '''

    def __init__(self, *args, **kwargs):
        factory_cls = kwargs.pop('factory_cls', None)
        if factory_cls is None:
            raise ValueError()
        kwargs['max_length'] = 255
        kwargs['choices'] = factory_cls.get_choices()
        super(HandlerField, self).__init__(*args, **kwargs)
        self.factory_cls = factory_cls

    def contribute_to_class(self, cls, name):
        CharField.contribute_to_class(self, cls, name)
        setattr(cls._meta, '%s_factory_cls' % name, self.factory_cls)

        ## cdchen-20120902: 必須用 curry(<全域函數>) 的方式才能 Work!!
        attr_name = 'create_%s' % name
        if not name.endswith('handler'):
            attr_name += '_handler'
        setattr(cls, attr_name,
            curry(_create_FIELD_handler, field=self),
        )


def _create_FIELD_handler(self, field, *args, **kwargs):
    '''
    建立 Handler 的函數。

    @param self: Model Instance.
    @param field: HandlerField Instance.
    @param args: Handler 的不定長度參數。
    @param kwargs: Handler 的不定長度的 name args。
    '''
    field_name = field.attname
    value = getattr(self, field_name)
    factory_cls = getattr(self._meta, '%s_factory_cls' % field_name)
    return factory_cls.create_handler(
        value, *args, **kwargs
    )

##
## LanguageField
##


class LanguageField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'max_length': 7,
            'choices': settings.LANGUAGES,
            'default': settings.LANGUAGE_CODE,
        })
        super(CharField, self).__init__(*args, **kwargs)


# End of file.
