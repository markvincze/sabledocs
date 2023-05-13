from pprint import pformat


class CodeItem:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.description_html = ''
        self.source_file_path = ''
        self.line_number = 0
        self.repository_url = ''


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
        self.fields: list[MessageField] = []
        self.parent_message = None
        self.package = None
        self.type_kind = "MESSAGE"

    @property
    def full_type(self):
        return self.full_name

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
        self.values: list[EnumValue] = []
        self.parent_message = None
        self.package = None
        self.type_kind = "ENUM"

    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)


class ServiceMethodArgument(CodeItem):
    def __init__(self, type: str, full_type: str, type_kind: str):
        CodeItem.__init__(self)
        self.type = type
        self.full_type = full_type
        self.type_kind = type_kind
        self.package = None


class ServiceMethod(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.request = ServiceMethodArgument("", "", "")
        self.response = ServiceMethodArgument("", "", "")


class Service(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.full_name = ''
        self.methods: list[ServiceMethod] = []


class Package(CodeItem):
    def __init__(self):
        CodeItem.__init__(self)
        self.messages = []
        self.enums = []
        self.services = []

    def __repr__(self):
        return pformat(vars(self), indent=4, width=1)


class LocationInfo:
    def __init__(self, line_number, comments):
        self.line_number = line_number
        self.comments = comments


class SableContext:
    def __init__(self, packages: list[Package], all_messages: list[Message], all_enums: list[Enum]):
        self.packages = packages
        self.all_messages = all_messages
        self.all_enums = all_enums

