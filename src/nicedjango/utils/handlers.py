# -*- coding: utf-8 -*-

'''
nicedjango.utils.handlers

All rights reserved for niceStudio.

class FooHandler(HandlerBase):

    pass


class BooHandler(FooHandler):

    class Meta:
        display_text = 'boo'
        description = ''


[ohighpass.myhandler_factory]
boo_handler = BooHandler

class MyHandlerFactory(HandlerFactory):

    class Meta:
        group_id = 'ohighpass.myhandler_factory'


factory = MyHandlerFactory()
handler = factory.get_handler('boo')     # handler is the BooHandler
factory.get_choices()                    # 'boo_handler' => 'boo'

'''

from nicedjango.utils.loaders import ClassLoader
import pprint


class Meta(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        results = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                results[key] = value
        return pprint.pformat(results)


class HandlerBaseMetaclass(type):

    def __new__(cls, name, bases, attrs):
        meta_cls = attrs.pop('Meta', object)
        meta_attrs = {}
        for key, value in meta_cls.__dict__.items():
            if key.startswith('_'):
                continue
            meta_attrs[key] = value
        attrs['_meta'] = Meta(**meta_attrs)
        return type.__new__(cls, name, bases, attrs)


class HandlerBase(object):

    __metaclass__ = HandlerBaseMetaclass


class HandlerFactoryMetaclass(type):

    def __new__(cls, name, bases, attrs):
        meta_cls = attrs.pop('Meta', object)
        meta_attrs = {}
        for key in dir(meta_cls):
            if key.startswith('_'):
                continue
            value = getattr(meta_cls, key)
            meta_attrs[key] = value
        group_id = meta_attrs.get('group_id', None)
        meta_attrs['handler_classes'] = {}
        handler_choices = []
        if group_id is not None:
            handler_classes = ClassLoader.load_name_and_classes(group_id)
            for name, handler_cls in handler_classes.items():
                meta_attrs['handler_classes'][name] = handler_cls
                if hasattr(handler_cls._meta, 'display_text'):
                    choices = (name, handler_cls._meta.display_text)
                else:
                    choices = (name, handler_cls.__name__)
                handler_choices.append(choices)
        meta_attrs['handler_choices'] = tuple(handler_choices)
        attrs['_meta'] = Meta(**meta_attrs)
        return type.__new__(cls, name, bases, attrs)


class HandlerFactory(object):

    __metaclass__ = HandlerFactoryMetaclass

    @classmethod
    def create_handler(cls, name, *args, **kwargs):
        handler_cls = cls._meta.handler_classes.get(name)
        if handler_cls is None:
            return None
        return handler_cls(*args, **kwargs)

    @classmethod
    def get_choices(cls):
        return cls._meta.handler_choices



# End of file