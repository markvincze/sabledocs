from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor_pb2 import EnumDescriptorProto
from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import MethodDescriptorProto
from proto_model import MessageField
from proto_model import Message
from proto_model import EnumValue
from proto_model import Enum
from proto_model import ServiceMethod
from proto_model import Service
from proto_model import Package
from proto_model import SableContext
import pprint
import markdown

COMMENT_PACKAGE_INDEX = 2
COMMENT_MESSAGE_INDEX = 4
COMMENT_ENUM_INDEX = 5
COMMENT_SERVICE_INDEX = 6
COMMENT_EXTENSION_INDEX = 7

COMMENT_MESSAGE_FIELD_INDEX = 2
COMMENT_MESSAGE_MESSAGE_INDEX = 3
COMMENT_MESSAGE_ENUM_INDEX = 4
COMMENT_MESSAGE_EXTENSION_INDEX = 6

COMMENT_ENUM_VALUE_INDEX = 2

COMMENT_SERVICE_METHOD_INDEX = 2

FIELD_TYPE_MESSAGE = 11
FIELD_TYPE_ENUM = 14


class ParseContext:
    def __init__(self, package, path, comments):
        self.package = package
        self.path = path
        self.comments = comments

    @classmethod
    def New(cls, package, comments):
        return ParseContext(package, "", comments)

    def WithPath(self, path):
        return ParseContext(self.package, path, self.comments)

    def ExtendPath(self, *path):
        return ParseContext(self.package, f"{self.path}.{'.'.join(map(str, path))}", self.comments)

    def GetComments(self, path=""):
        return self.comments.get(self.path if path == "" else path, "")


def parse_enum(enum: EnumDescriptorProto, ctx: ParseContext, nested_type_chain: str):
    def parse_enum_value(enum_value: EnumValueDescriptorProto, ctx: ParseContext):
        ev = EnumValue()
        ev.name = enum_value.name
        ev.number = enum_value.number
        ev.description = ctx.GetComments()
        ev.description_html = markdown.markdown(ev.description)

        return ev

    e = Enum()
    e.name = enum.name
    e.full_name = f"{ctx.package.name}.{nested_type_chain}{enum.name}"
    e.description = ctx.GetComments()
    e.description_html = markdown.markdown(e.description)
    for i, ev in enumerate(enum.value):
        e.values.append(parse_enum_value(ev, ctx.ExtendPath(COMMENT_ENUM_VALUE_INDEX, i)))

    return e


def parse_enums(enums: list[EnumDescriptorProto], ctx: ParseContext, nested_type_chain: str):
    for (i, enum) in enumerate(enums):
        ctx.package.enums.append(parse_enum(enum, ctx.ExtendPath(i), nested_type_chain))

    ctx.package.enums.sort(key=lambda e: e.name)


def parse_field(field: FieldDescriptorProto, ctx: ParseContext):
    mf = MessageField()
    mf.name = field.name
    mf.number = field.number
    mf.label = to_label_name(field.label)
    mf.description = ctx.GetComments()
    mf.description_html = markdown.markdown(mf.description)
    mf.full_type = field.type_name.strip(".") if field.type_name != "" else to_type_name(field.type)
    mf.default_value = field.default_value
    mf.type = extract_type_name_from_full_name(field.type_name.strip(".")) if field.type_name != "" else to_type_name(field.type)
    mf.type_kind = "MESSAGE" if field.type == FIELD_TYPE_MESSAGE else "ENUM" if field.type == FIELD_TYPE_ENUM else "UNKNOWN"
    if mf.type.endswith("Entry"):
        entry_nested_type = next(filter(lambda m: m.name == mf.type, ctx.package.messages), None)
        if entry_nested_type is not None and entry_nested_type.is_map_entry:
            mf.type = f"map<{entry_nested_type.fields[0].type}, {entry_nested_type.fields[1].type}>"
            mf.full_type = f"map<{entry_nested_type.fields[0].type}, {entry_nested_type.fields[1].type}>"
            mf.label = ""

    return mf


def extract_type_name_from_full_name(full_type_name: str):
    last_dot = full_type_name.rfind(".")
    if last_dot == -1:
        return full_type_name
    else:
        return full_type_name[last_dot + 1:]


def parse_message(message: DescriptorProto, ctx: ParseContext, nested_type_chain: str):
    parse_messages(message.nested_type, ctx.ExtendPath(COMMENT_MESSAGE_MESSAGE_INDEX), f"{message.name}.")
    parse_enums(message.enum_type, ctx.ExtendPath(COMMENT_MESSAGE_ENUM_INDEX), f"{message.name}.")

    if message.oneof_decl:
        pprint.pprint(message.oneof_decl)

    m = Message()
    m.name = message.name
    m.full_name = f"{ctx.package.name}.{nested_type_chain}{message.name}"
    m.description = ctx.GetComments()
    m.description_html = markdown.markdown(m.description)
    m.is_map_entry = message.options.map_entry
    for i, mf in enumerate(message.field):
        m.fields.append(parse_field(mf, ctx.ExtendPath(COMMENT_MESSAGE_FIELD_INDEX, i)))

    m.fields.sort(key=lambda mf: mf.number)

    return m


def parse_messages(messages: list[DescriptorProto], ctx: ParseContext, nested_type_chain: str):
    for (i, message) in enumerate(messages):
        ctx.package.messages.append(parse_message(message, ctx.ExtendPath(i), nested_type_chain))

    ctx.package.messages.sort(key=lambda m: m.name)


def parse_service_method(service_method: MethodDescriptorProto, ctx: ParseContext):
    sm = ServiceMethod()
    sm.name = service_method.name
    sm.description = ctx.GetComments()
    sm.description_html = markdown.markdown(sm.description)
    sm.request_type = service_method.input_type[service_method.input_type.rfind(".") + 1:]
    sm.request_full_type = service_method.input_type
    sm.response_type = service_method.output_type[service_method.output_type.rfind(".") + 1:]
    sm.response_full_type = service_method.output_type

    return sm


def parse_service(service: ServiceDescriptorProto, ctx: ParseContext):
    s = Service()
    s.name = service.name
    s.full_name = f"{ctx.package.name}.{service.name}"
    s.description = ctx.GetComments()
    s.description_html = markdown.markdown(s.description)
    for i, service_method in enumerate(service.method):
        s.methods.append(parse_service_method(service_method, ctx.ExtendPath(COMMENT_SERVICE_METHOD_INDEX, i)))

    return s


def parse_services(services: list[ServiceDescriptorProto], ctx: ParseContext):
    for (i, service) in enumerate(services):
        ctx.package.services.append(parse_service(service, ctx.ExtendPath(i)))

    ctx.package.services.sort(key=lambda s: s.name)


def add_package_to_message_fields(messages: list[Message], packages):
    for m in messages:
        for mf in m.fields:
            if mf.full_type == "":
                continue

            package = next(filter(lambda p: mf.full_type.startswith(p.name), packages), None)
            if package is not None:
                mf.package = package


def build_comment_map(source_code_info):
    def has_comments(location):
        return location.leading_comments != '' or location.trailing_comments != ''

    def build_key(path):
        return '.'.join(map(lambda i: str(i), path))

    def scrub(comment: str):
        return comment.strip().replace(" \n", "\n")

    def build_comment(location):
        comment = ""
        if location.leading_comments != "":
            comment += scrub(location.leading_comments)
            comment += "\n\n"

        comment += scrub(location.trailing_comments)

        return comment.strip()

    comments = {}
    for l in source_code_info.location:
        if has_comments(l):
            comments[build_key(l.path)] = build_comment(l)

    return comments


def to_type_name(type: FieldDescriptorProto.Type):
    match type:
        case FieldDescriptorProto.Type.TYPE_BOOL: return "bool"
        case FieldDescriptorProto.Type.TYPE_DOUBLE: return "double"
        case FieldDescriptorProto.Type.TYPE_FLOAT: return "float"
        case FieldDescriptorProto.Type.TYPE_INT64: return "int64"
        case FieldDescriptorProto.Type.TYPE_UINT64: return "uint64"
        case FieldDescriptorProto.Type.TYPE_INT32: return "int32"
        case FieldDescriptorProto.Type.TYPE_FIXED64: return "fixed64"
        case FieldDescriptorProto.Type.TYPE_FIXED32: return "fixed32"
        case FieldDescriptorProto.Type.TYPE_BOOL: return "bool"
        case FieldDescriptorProto.Type.TYPE_STRING: return "string"
        case FieldDescriptorProto.Type.TYPE_GROUP: return "group"
        case FieldDescriptorProto.Type.TYPE_MESSAGE: return "message"
        case FieldDescriptorProto.Type.TYPE_BYTES: return "bytes"
        case FieldDescriptorProto.Type.TYPE_UINT32: return "uint32"
        case FieldDescriptorProto.Type.TYPE_ENUM: return "enum"
        case FieldDescriptorProto.Type.TYPE_SFIXED32: return "sfixed32"
        case FieldDescriptorProto.Type.TYPE_SFIXED64: return "sfixed64"
        case FieldDescriptorProto.Type.TYPE_SINT32: return "sint32"
        case FieldDescriptorProto.Type.TYPE_SINT64: return "sint64"
        case _: "unknown"


def to_label_name(type):
    match type:
        case FieldDescriptorProto.Label.LABEL_OPTIONAL: return "optional"
        case FieldDescriptorProto.Label.LABEL_REQUIRED: return "required"
        case FieldDescriptorProto.Label.LABEL_REPEATED: return "repeated"
        case _: ""

def parse_proto_descriptor(file_name):
    packages = dict()
    all_messages = []
    all_enums = []
    with open(file_name, mode="rb") as proto_descriptor_file:
        fds = FileDescriptorSet.FromString(proto_descriptor_file.read())
        for file in fds.file:
            print(f"Processing {file.name}")

            comments = build_comment_map(file.source_code_info)

            package = packages.get(file.package, Package())
            package.name = file.package

            ctx = ParseContext.New(package, comments)

            package.description += ctx.GetComments(str(COMMENT_PACKAGE_INDEX))
            # pprint.pprint(comments)

            parse_enums(file.enum_type, ctx.WithPath(COMMENT_ENUM_INDEX), "")
            parse_messages(file.message_type, ctx.WithPath(COMMENT_MESSAGE_INDEX), "")
            parse_services(file.service, ctx.WithPath(COMMENT_SERVICE_INDEX))

            all_messages.extend(package.messages)
            all_enums.extend(package.enums)

            packages[file.package] = package

        add_package_to_message_fields(all_messages, packages.values())


        return SableContext(
            sorted(
                packages.values(),
                key=lambda p: (p.name)),
            all_messages,
            all_enums)

