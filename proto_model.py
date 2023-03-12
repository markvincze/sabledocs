from pprint import pformat


class CodeItem:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.description_html = ''
        self.source_file_path = ''
        self.line_number = 0


class MessageField(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.number = 0
        self.label = ''
        self.type = ''
        self.full_type = ''
        self.default_value = ''
        self.package = None
        self.type_kind = "UNKNOWN"

    def __repr__(self):
        filtered_vars = dict(filter(lambda elem: elem[0] != "package", vars(self).items()))
        return pformat(filtered_vars, indent=4, width=1)


class Message(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.full_name = ''
        self.is_map_entry = False
        self.fields = []

    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)


class EnumValue(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.number = 0


class Enum(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.full_name = ''
        self.values = []

    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)


class ServiceMethod(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.request_type = ''
        self.request_full_type = ''
        self.response_type = ''
        self.response_full_type = ''


class Service(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.full_name = ''
        self.methods = []


class Package(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.messages = []
        self.enums = []
        self.services = []

    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)


class LocationInfo:
    def __init__(self, line_number, comment):
        self.line_number = 0
        self.comments = ""


class SableContext:
    def __init__(self, packages, all_messages, all_enums):
        self.packages = packages
        self.all_messages = all_messages
        self.all_enums = all_enums

