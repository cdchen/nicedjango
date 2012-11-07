# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models.fields import CharField, NOT_PROVIDED
from django.db.models.fields.subclassing import SubfieldBase
from django.utils.functional import curry
from uuidfield.fields import UUIDField, StringUUID
import shortuuid

#from django_extensions.db.fields import UUIDField


class ShortUUID(StringUUID):

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return shortuuid.encode(self)


class ShortUUIDField(UUIDField):
    '''
    用來產生適合 HTTP 使用的 UUID 欄位。

    注意事項：

    若需要搭配 django.contrib.admin 的 template 時，必須將
    templates/admin/edit_inline/*.html 的：

        {% if inline_admin_form.has_auto_field %}
            {{ inline_admin_form.pk_field.field }}
        {% endif %}

    改為：

        {% if inline_admin_form.pk_field %}
            {{ inline_admin_form.pk_field.field }}
        {% endif %}

    否則將會丟出 MultiValueDictKeyError 的錯誤。
    '''

    __metaclass__ = SubfieldBase

    def get_internal_type(self):
        return 'ShortUUIDField'

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if self.auto and add and not value:
            uuid = self._create_uuid()
            value = shortuuid.encode(uuid)
            setattr(model_instance, self.attname, value)
        return value

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, basestring):
            return ShortUUID(shortuuid.decode(value).hex)
        return value

#    def contribute_to_class(self, cls, name):
#        if self.primary_key:
#            assert not cls._meta.has_auto_field, \
#              "A model can't have more than one AutoField: %s %s %s; have %s" % \
#               (self, cls, name, cls._meta.auto_field)
#            super(ShortUUIDField, self).contribute_to_class(cls, name)
#            cls._meta.has_auto_field = True
#            cls._meta.auto_field = self
#        else:
#            super(ShortUUIDField, self).contribute_to_class(cls, name)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)


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

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)


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

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

# End of file.
