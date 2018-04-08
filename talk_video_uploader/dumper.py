import collections

import yaml


def yaml_dump(data):
    return yaml.dump(data, Dumper=EventDumper)


def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())


class EventDumper(yaml.SafeDumper):
    def __init__(self, *args, **kwargs):
        kwargs["default_flow_style"] = False
        kwargs["allow_unicode"] = True
        super(EventDumper, self).__init__(*args, **kwargs)


EventDumper.add_representer(collections.OrderedDict, _dict_representer)
