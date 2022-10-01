from pprint import pformat

class MessageField:
    def __init__(self):
        self.name = ''
        self.number = 0
        self.label = ''
        self.description = ''
        self.type = ''
        self.full_type = ''
        self.default_value = ''

class Message:
    def __init__(self):
        self.name = ''
        self.full_name = ''
        self.description = ''
        self.fields = []

class EnumValue:
    def __init__(self):
        self.name = ''
        self.number = 0
        self.description = ''

class Enum:
    def __init__(self):
        self.name = ''
        self.full_name = ''
        self.description = ''
        self.values = []
    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)

class ServiceMethod:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.request_type = ''
        self.request_full_type = ''
        self.response_type = ''
        self.response_full_type = ''

class Service:
    def __init__(self):
        self.name = ''
        self.full_name = ''
        self.description = ''
        self.methods = []

class Package:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.messages = []
        self.enums = []
        self.services = []
    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)
