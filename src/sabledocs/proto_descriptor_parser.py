from typing import Dict, Sequence
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor_pb2 import EnumDescriptorProto
from google.protobuf.descriptor_pb2 import EnumValueDescriptorProto
from google.protobuf.descriptor_pb2 import DescriptorProto
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.descriptor_pb2 import MethodDescriptorProto
from sabledocs.proto_model import MessageField, Message, EnumValue, Enum, OneOfFieldGroup, ServiceMethod, ServiceMethodArgument, Service, Package, LocationInfo, SableContext
from sabledocs.sable_config import MemberOrdering, RepositoryType, SableConfig
import pprint
import markdown
import pprint
import re
from furl import furl

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


def build_source_code_url(repository_url, repository_type, repository_branch, repository_dir, file_path, line_number):
    match repository_type:
        case RepositoryType.NONE:
            return None
        case RepositoryType.GITHUB:
            # ex: https://git.example.com/blob/main/myrepodir/foo/bar.proto#L41
            u = furl(repository_url) / 'blob' / repository_branch / repository_dir / file_path
            u.fragment.add(f"L{line_number + 1}")
            u.path.normalize()
            return u.url
        case RepositoryType.BITBUCKET:
            # ex: https://git.example.com/src/main/foo/bar.proto#lines-42
            u = furl(repository_url) / 'src' / repository_branch / repository_dir / file_path
            u.fragment.add(f"lines-{line_number + 1}")
            u.path.normalize()
            return u.url
        case RepositoryType.BITBUCKET_DATA_CENTER:
            # ex: https://bitbucket.corp.mycompany.com/projects/MYTEAM/repos/myreponame/browse/foo/bar.proto#42
            u = furl(repository_url) / 'browse' / repository_dir / file_path
            u.fragment.add(f"{line_number + 1}")
            u.path.normalize()
            return u.url
        case RepositoryType.GITLAB:
            # ex: https://git.example.com/-/blob/main/myrepodir/foo/bar.proto#L41
            u = furl(repository_url) / '-' / 'blob' / repository_branch / repository_dir / file_path
            u.fragment.add(f"L{line_number}")
            u.path.normalize()
            return u.url
    return ""


class ParseContext:
    def __init__(self, config, package, source_file_path, path, locations):
        self.config = config
        self.package = package
        self.source_file_path = source_file_path
        self.path = path
        self.locations = locations

    @classmethod
    def New(cls, config, package, source_file_path, locations):
        return ParseContext(config, package, source_file_path, "", locations)

    def WithPath(self, path):
        return ParseContext(self.config, self.package, self.source_file_path, path, self.locations)

    def ExtendPath(self, *path):
        return ParseContext(self.config, self.package, self.source_file_path, f"{self.path}.{'.'.join(map(str, path))}", self.locations)

    def GetComments(self, path=""):
        location = self.locations.get(self.path if path == "" else path, None)
        if location is None:
            return ""
        else:
            comments = location.comments
            for ignore_after in self.config.ignore_comments_after:
                comments = comments.split(ignore_after)[0]
            for ignore_line in self.config.ignore_comment_lines_containing:
                comments = '\n'.join([c for c in comments.splitlines() if ignore_line not in c])
            return comments

    def GetLineNumber(self, path=""):
        location = self.locations.get(self.path if path == "" else path, None)
        return 0 if location is None else location.line_number


def parse_enum(enum: EnumDescriptorProto, ctx: ParseContext, parent_message, nested_type_chain: str):
    def parse_enum_value(enum_value: EnumValueDescriptorProto, ctx: ParseContext):
        ev = EnumValue()
        ev.name = enum_value.name
        ev.number = enum_value.number
        ev.description = ctx.config.comments_parser.ParseEnumValue(ctx.GetComments())
        ev.description_html = markdown_to_html(ev.description, ctx.config)
        ev.line_number = ctx.GetLineNumber()

        return ev

    e = Enum()
    e.name = enum.name
    e.full_name = f"{ctx.package.name}.{nested_type_chain}{enum.name}".lstrip(".")
    e.parent_message = parent_message
    e.description = ctx.config.comments_parser.ParseEnum(ctx.GetComments())
    e.description_html = markdown_to_html(e.description, ctx.config)
    e.source_file_path = ctx.source_file_path
    e.line_number = ctx.GetLineNumber()
    e.repository_url = build_source_code_url(
        ctx.config.repository_url,
        ctx.config.repository_type,
        ctx.config.repository_branch,
        ctx.config.repository_dir,
        e.source_file_path,
        e.line_number)

    for i, ev in enumerate(enum.value):
        e.values.append(parse_enum_value(ev, ctx.ExtendPath(COMMENT_ENUM_VALUE_INDEX, i)))

    return e


def parse_enums(enums: Sequence[EnumDescriptorProto], ctx: ParseContext, parent_message, nested_type_chain: str):
    for (i, enum) in enumerate(enums):
        ctx.package.enums.append(parse_enum(enum, ctx.ExtendPath(i), parent_message, nested_type_chain))

    if ctx.config.member_ordering == MemberOrdering.ALPHABETICAL:
        ctx.package.enums.sort(key=lambda e: e.name)


def parse_field(field: FieldDescriptorProto, containing_message: DescriptorProto, ctx: ParseContext):
    mf = MessageField()
    mf.name = field.name

    mf.number = field.number
    mf.label = to_label_name(field.label, field.proto3_optional)
    mf.description = ctx.config.comments_parser.ParseField(ctx.GetComments())
    mf.description_html = markdown_to_html(mf.description, ctx.config)
    mf.line_number = ctx.GetLineNumber()
    mf.full_type = field.type_name.strip(".") if field.type_name != "" else to_type_name(field.type)
    mf.default_value = field.default_value
    mf.type = extract_type_name_from_full_name(field.type_name.strip(".")) if field.type_name != "" else to_type_name(field.type)
    mf.type_kind = "MESSAGE" if field.type == FIELD_TYPE_MESSAGE else "ENUM" if field.type == FIELD_TYPE_ENUM else "UNKNOWN"

    if mf.type.endswith("Entry"):
        entry_nested_type = next(filter(lambda m: m.full_name == mf.full_type, ctx.package.messages), None)
        if entry_nested_type is not None and entry_nested_type.is_map_entry:
            mf.type = f"map<{entry_nested_type.fields[0].type}, {entry_nested_type.fields[1].type}>"
            mf.full_type = f"map<{entry_nested_type.fields[0].type}, {entry_nested_type.fields[1].type}>"
            mf.label = ""

    # We only set the oneof name if the field is not a Proto3 optional.
    # Proto3 optionals are represented as a "synthetic" oneof, which does nto need to be displayed in the docs.
    if field.HasField("oneof_index") and not field.proto3_optional:
        mf.oneof_name = containing_message.oneof_decl[field.oneof_index].name

    return mf


def extract_type_name_from_full_name(full_type_name: str):
    last_dot = full_type_name.rfind(".")
    if last_dot == -1:
        return full_type_name
    else:
        return full_type_name[last_dot + 1:]


def parse_message(message: DescriptorProto, ctx: ParseContext, parent_message, nested_type_chain: str):
    m = Message()
    m.name = message.name
    m.full_name = f"{ctx.package.name}.{nested_type_chain}{message.name}".lstrip(".")
    m.parent_message = parent_message
    m.description = ctx.config.comments_parser.ParseMessage(ctx.GetComments())
    m.description_html = markdown_to_html(m.description, ctx.config)
    m.source_file_path = ctx.source_file_path
    m.line_number = ctx.GetLineNumber()
    m.repository_url = build_source_code_url(
        ctx.config.repository_url,
        ctx.config.repository_type,
        ctx.config.repository_branch,
        ctx.config.repository_dir,
        m.source_file_path,
        m.line_number)

    # NOTE: The processing of nested types have to happen before processing the fields, to have the Entry nested types representing maps already present.
    new_nested_type_chain = f"{nested_type_chain}{message.name}."
    parse_messages(message.nested_type, ctx.ExtendPath(COMMENT_MESSAGE_MESSAGE_INDEX), m, new_nested_type_chain)
    parse_enums(message.enum_type, ctx.ExtendPath(COMMENT_MESSAGE_ENUM_INDEX), m, new_nested_type_chain)

    m.is_map_entry = message.options.map_entry
    for i, mf in enumerate(message.field):
        m.fields.append(parse_field(mf, message, ctx.ExtendPath(COMMENT_MESSAGE_FIELD_INDEX, i)))

    if ctx.config.member_ordering == MemberOrdering.ALPHABETICAL:
        m.fields.sort(key=lambda mf: mf.number)

    oneof_names = set([f.oneof_name for f in m.fields if f.oneof_name])
    m.oneof_field_groups = list(map(
        lambda n: OneOfFieldGroup(n, list(filter(lambda f: f.oneof_name == n, m.fields))),
        oneof_names))

    return m


def parse_messages(messages: Sequence[DescriptorProto], ctx: ParseContext, parent_message, nested_type_chain: str):
    for (i, message) in enumerate(messages):
        ctx.package.messages.append(parse_message(message, ctx.ExtendPath(i), parent_message, nested_type_chain))

    if ctx.config.member_ordering == MemberOrdering.ALPHABETICAL:
        ctx.package.messages.sort(key=lambda m: m.name)


def parse_service_method(service_method: MethodDescriptorProto, ctx: ParseContext):
    sm = ServiceMethod()
    sm.name = service_method.name
    sm.description = ctx.config.comments_parser.ParseServiceMethod(ctx.GetComments())
    sm.description_html = markdown_to_html(sm.description, ctx.config)
    sm.line_number = ctx.GetLineNumber()
    sm.request = ServiceMethodArgument(
        service_method.input_type[service_method.input_type.rfind(".") + 1:],
        service_method.input_type.strip("."),
        "MESSAGE"
    )

    sm.response = ServiceMethodArgument(
        service_method.output_type[service_method.output_type.rfind(".") + 1:],
        service_method.output_type.strip("."),
        "MESSAGE"
    )

    return sm


def parse_service(service: ServiceDescriptorProto, ctx: ParseContext):
    s = Service()
    s.name = service.name
    s.full_name = f"{ctx.package.name}.{service.name}".lstrip(".")
    s.description = ctx.config.comments_parser.ParseService(ctx.GetComments())
    s.description_html = markdown_to_html(s.description, ctx.config)
    s.source_file_path = ctx.source_file_path
    s.line_number = ctx.GetLineNumber()
    s.repository_url = build_source_code_url(
        ctx.config.repository_url,
        ctx.config.repository_type,
        ctx.config.repository_branch,
        ctx.config.repository_dir,
        s.source_file_path,
        s.line_number)
    for i, service_method in enumerate(service.method):
        s.methods.append(parse_service_method(service_method, ctx.ExtendPath(COMMENT_SERVICE_METHOD_INDEX, i)))

    return s


def parse_services(services: Sequence[ServiceDescriptorProto], ctx: ParseContext):
    for (i, service) in enumerate(services):
        ctx.package.services.append(parse_service(service, ctx.ExtendPath(i)))

    if ctx.config.member_ordering == MemberOrdering.ALPHABETICAL:
        ctx.package.services.sort(key=lambda s: s.name)


def extract_package_name_from_full_name(full_type_name: str):
    last_dot = full_type_name.rfind(".")
    if last_dot == -1:
        return ""
    else:
        return full_type_name[:last_dot]


def add_package_references(messages: list[Message], services: list[Service], packages: list[Package], hidden_packages: list[str]):
    def find_matching_package(full_type_name):
            # We sort the matching packages by the length of their name, and pick the longest.
            # This is needed, because if we have a package foo, and a package foo.bar, and a type foo.bar.Baz,
            # then we could incorrectly pick the package foo instead of foo.bar.
            filtered = sorted(filter(lambda p: full_type_name.startswith(p.name), packages), key=lambda package: len(package.name), reverse=True)
            return None if len(filtered) == 0 else filtered[0]

    for m in messages:
        package = find_matching_package(m.full_type)
        if package is not None:
            m.package = package

        for mf in m.fields:
            if mf.full_type == "":
                continue

            package = find_matching_package(mf.full_type)
            if package is not None:
                mf.package = package
                mf.is_package_hidden = any(filter(lambda p: mf.full_type.startswith(p), hidden_packages))

    for s in services:
        for sm in s.methods:
            requestPackage = next(filter(lambda p: extract_package_name_from_full_name(sm.request.full_type) == p.name, packages), None)
            if requestPackage is not None:
                sm.request.package = requestPackage

            responsePackage = next(filter(lambda p: extract_package_name_from_full_name(sm.response.full_type) == p.name, packages), None)
            if responsePackage is not None:
                sm.response.package = responsePackage


def build_location_map(source_code_info):
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

    def build_location_info(location):
        return LocationInfo(location.span[0], build_comment(location))

    location_infos = {}
    for loc in source_code_info.location:
        location_infos[build_key(loc.path)] = build_location_info(loc)

    return location_infos


def to_type_name(type: FieldDescriptorProto.Type.ValueType):
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
        case _: return "unknown"


def to_label_name(type, proto3_optional):
    if proto3_optional:
        return "optional"
    match type:
        case FieldDescriptorProto.Label.LABEL_REQUIRED: return "required"
        case FieldDescriptorProto.Label.LABEL_REPEATED: return "repeated"
        case _: return ""


def parse_proto_descriptor(sable_config: SableConfig):
    packages: Dict[str, Package] = dict()
    all_messages = []
    all_enums = []
    all_services = []

    print()
    with open(sable_config.input_descriptor_file, mode="rb") as proto_descriptor_file:
        fds = FileDescriptorSet.FromString(proto_descriptor_file.read())
        for file in fds.file:
            print(f"Processing {file.name}")

            locations = build_location_map(file.source_code_info)

            package = packages.get(file.package, Package())
            package.name = file.package

            ctx = ParseContext.New(sable_config, package, file.name, locations)

            package.description += sable_config.comments_parser.ParsePackage(ctx.GetComments(str(COMMENT_PACKAGE_INDEX)))
            package.description_html = markdown_to_html(package.description, sable_config)

            parse_enums(file.enum_type, ctx.WithPath(COMMENT_ENUM_INDEX), None, "")
            parse_messages(file.message_type, ctx.WithPath(COMMENT_MESSAGE_INDEX), None, "")
            parse_services(file.service, ctx.WithPath(COMMENT_SERVICE_INDEX))

            all_messages.extend(package.messages)
            all_enums.extend(package.enums)
            all_services.extend(package.services)

            packages[file.package] = package

        add_package_references(all_messages, all_services, list(packages.values()), sable_config.hidden_packages)

        return SableContext(
            sorted(packages.values(), key=lambda p: (p.name))
                if sable_config.member_ordering == MemberOrdering.ALPHABETICAL
                else packages.values(),
            all_messages,
            all_enums,
            sable_config)


def markdown_to_html(md: str, sable_config: SableConfig):
    # We trim single spaces at the beginning of lines, because those are most probably due to the common pattern of
    # having a single space between // and the start of the comment line in code comments.
    # And the single leading space causes problems with the markdown parsing, particularly with fenced code blocks.
    # But removing every leading space is not always correct, because the comments might look like this:
    # //This is a comment
    # //
    # //    This is a code block
    # //
    # //This is after the code block
    # If we always removed one leading space from every line, in the above example that would change the indentation
    # from 4 spaces to 3, thus the code block would not work.
    # Due to this, we only do this if every line has at least one leading space, that's a strong indication that
    # they should be trimmed.
    if all(map(lambda l: l == "" or l.startswith(" "), md.split("\n")[1:])):
        md = re.sub(r"^ ", r"", md, flags=re.MULTILINE)

    return markdown.markdown(md, extensions=sable_config.markdown_extensions)
