# -*- coding: utf-8 -*-

'''
nicedjango.utils.loaders

All rights reserved for niceStudio.
'''

import pkg_resources


class ClassLoader(object):

    @classmethod
    def load_classes(cls, group, name=None):
        return [
            ep.load()
            for ep in pkg_resources.iter_entry_points(group, name)
        ]

    @classmethod
    def load_name_and_classes(cls, group):
        results = {}
        for ep in pkg_resources.iter_entry_points(group):
            results[ep.name] = ep.load()
        return results


# End of file.
