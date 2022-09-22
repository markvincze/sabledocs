import json
from proto_model import *

def parse_enum(json_enum):
    def parse_enum_value(json_enum_value):
        ev = EnumValue()
        ev.name = json_enum_value['name']
        ev.number = json_enum_value['number']
        ev.description = json_enum_value['description']
        return ev

    e = Enum()
    e.name = json_enum['name']
    e.full_name = json_enum['fullName']
    e.description = json_enum['description']
    e.values = map(parse_enum_value, json_enum['values'])

    return e

def parse_field(json_field):
    mf = MessageField()
    mf.name = json_field['name']
    mf.label = json_field['label']
    mf.description = json_field['description']
    mf.type = json_field['type']
    mf.full_type = json_field['fullType']
    mf.default_value = json_field['defaultValue']
    return mf

def parse_message(json_message):
    m = Message()
    m.name = json_message['name']
    m.full_name = json_message['fullName']
    m.description = json_message['description']
    m.fields = map(parse_field, json_message['fields'])

    return m

def parse_service_method(json_service_method):
    sm = ServiceMethod()
    sm.name = json_service_method['name']
    sm.description = json_service_method['description']
    sm.request_type = json_service_method['requestType']
    sm.request_full_type = json_service_method['requestType']
    sm.response_type = json_service_method['requestType']
    sm.response_full_type = json_service_method['requestType']

def parse_service(json_service):
    s = Service()
    s.name = json_service['name']
    s.full_name = json_service['fullName']
    s.description = json_service['description']
    s.methods = map(parse_service_method, json_service['methods'])

def parse_proto_json(file_name):
    with open(file_name) as proto_json_file:
        proto_data = json.load(proto_json_file)

        packages = dict()
        for file in proto_data['files']:
            package_name = file['package']
            package = packages.get(package_name, Package())
            package.name = package_name
            package.description += file['description']
            package.enums.extend(map(parse_enum, file['enums']))
            package.messages.extend(map(parse_message, file['messages']))
            package.services.extend(map(parse_service, file['services']))

            packages[package_name] = package

        # values = packages.values()

        return sorted(
            packages.values(),
            key=lambda p: (p.name))

