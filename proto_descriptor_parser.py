from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor_pb2 import EnumDescriptorProto
from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import MethodDescriptorProto
from proto_model import *
import pprint

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

    def GetComments(self, path = ""):
        return self.comments.get(self.path if path == "" else path, "")

def parse_enum(enum: EnumDescriptorProto, ctx: ParseContext):
    def parse_enum_value(enum_value: EnumValueDescriptorProto, ctx: ParseContext):
        ev = EnumValue()
        ev.name = enum_value.name
        ev.number = enum_value.number
        ev.description = ctx.GetComments()

        return ev

    e = Enum()
    e.name = enum.name
    e.full_name = f"{ctx.package}.{enum.name}"
    e.description = ctx.GetComments()
    for i, ev in enumerate(enum.value):
        e.values.append(parse_enum_value(ev, ctx.ExtendPath(COMMENT_ENUM_VALUE_INDEX, i)))

    return e

def parse_enums(enums: list[EnumDescriptorProto], ctx: ParseContext):
    result = []
    for (i, enum) in enumerate(enums):
        result.append(parse_enum(enum, ctx.ExtendPath(i)))

    return result

def parse_field(field: FieldDescriptorProto, ctx: ParseContext):
    mf = MessageField()
    mf.name = field.name
    mf.number = field.number
    mf.label = to_label_name(field.label)
    mf.description = ctx.GetComments()
    mf.type = field.type_name.strip(".") if field.type_name != "" else to_type_name(field.type)
    mf.default_value = field.default_value

    return mf

def parse_message(message: DescriptorProto, ctx: ParseContext):
    m = Message()
    m.name = message.name
    m.full_name = f"{ctx.package}.{message.name}"
    m.description = ctx.GetComments()
    for i, mf in enumerate(message.field):
        m.fields.append(parse_field(mf, ctx.ExtendPath(COMMENT_MESSAGE_FIELD_INDEX, i)))

    return m

def parse_messages(messages: list[DescriptorProto], ctx: ParseContext):
    result = []
    for (i, message) in enumerate(messages):
        result.append(parse_message(message, ctx.ExtendPath(i)))

    return result

def parse_service_method(service_method: MethodDescriptorProto, ctx: ParseContext):
    sm = ServiceMethod()
    sm.name = service_method.name
    sm.description = ctx.GetComments()
    sm.request_type = service_method.input_type[service_method.input_type.rfind(".") + 1:]
    sm.request_full_type = service_method.input_type
    sm.response_type = service_method.output_type[service_method.output_type.rfind(".") + 1:]
    sm.response_full_type = service_method.output_type

    return sm

def parse_service(service: ServiceDescriptorProto, ctx: ParseContext):
    s = Service()
    s.name = service.name
    s.full_name = f"{ctx.package}.{service.name}"
    s.description = ctx.GetComments()
    for i, service_method in enumerate(service.method):
        s.methods.append(parse_service_method(service_method, ctx.ExtendPath(COMMENT_SERVICE_METHOD_INDEX, i)))

    return s

def parse_services(services: list[ServiceDescriptorProto], ctx: ParseContext):
    result = []
    for (i, service) in enumerate(services):
        result.append(parse_service(service, ctx.ExtendPath(i)))

    return result

def parse_proto_descriptor(file_name):
    packages = dict()
    with open(file_name, mode="rb") as proto_descriptor_file:
        fds = FileDescriptorSet.FromString(proto_descriptor_file.read())
        for file in fds.file:

            comments = build_comment_map(file.source_code_info)
            ctx = ParseContext.New(file.package, comments)

            package = packages.get(file.package, Package())
            package.name = file.package
            package.description += ctx.GetComments(str(COMMENT_PACKAGE_INDEX))
            pprint.pprint(comments)

            package.enums.extend(parse_enums(file.enum_type, ctx.WithPath(COMMENT_ENUM_INDEX)))
            package.messages.extend(parse_messages(file.message_type, ctx.WithPath(COMMENT_MESSAGE_INDEX)))
            package.services.extend(parse_services(file.service, ctx.WithPath(COMMENT_SERVICE_INDEX)))

            packages[file.package] = package
            print(file.name)

        return sorted(
            packages.values(),
            key=lambda p: (p.name))

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

def to_label_name(type: FieldDescriptorProto.Label):
    match type:
        case FieldDescriptorProto.Label.LABEL_OPTIONAL: return "optional"
        case FieldDescriptorProto.Label.LABEL_REQUIRED: return "required"
        case FieldDescriptorProto.Label.LABEL_REPEATED: return "repeated"
        case _: ""

