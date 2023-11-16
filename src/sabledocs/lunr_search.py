import lunr
from sabledocs.proto_model import Enum, Message, Package, SableContext, Service


def build_search_index(sable_context: SableContext) -> tuple[dict[str, dict[str, str]], lunr.index.Index]:
    documents = []

    for package in sable_context.packages:
        doc = {
            "package": package.name,
            "url": f"{package.name}.html",
            "content": build_package_content(package)
        }

        documents.append(doc)

    builder = lunr.get_default_builder()
    #builder.metadata_whitelist.append("position") This can be enabled to get position information in the search results, not used yet.

    idx = lunr.lunr(
        ref="package", fields=("content", "content", "url"), documents=documents, builder=builder
    )

    documents_dict = {d["package"]:d for d in documents}

    return (documents_dict, idx)


def build_package_content(package: Package):
    acc = ""
    acc += package.name + "\n"
    acc += package.description + "\n"
    for service in package.services:
        acc = append_service_content(acc, service)

    for message in package.messages:
        acc = append_message_content(acc, message)

    for enum in package.enums:
        acc = append_enum_content(acc, enum)
    
    return acc


def append_service_content(acc: str, service: Service):
    for name_segment in service.full_name.split("."):
        acc += name_segment + "\n"

    acc += service.description + "\n"
    for method in service.methods:
        acc += method.name + "\n"
        acc += method.description + "\n"
        for name_segment in method.request.full_type.split("."):
            acc += name_segment + "\n"

        for name_segment in method.response.full_type.split("."):
            acc += name_segment + "\n"
    
    return acc


def append_message_content(acc: str, message: Message):
    for name_segment in message.full_name.split("."):
        acc += name_segment + "\n"

    for field in message.fields:
        acc += field.name + "\n"
        acc += field.description + "\n"
    
    return acc


def append_enum_content(acc: str, enum: Enum):
    for name_segment in enum.full_name.split("."):
        acc += name_segment + "\n"

    acc += enum.description + "\n"
    for value in enum.values:
        acc += value.name + "\n"
        acc += value.description + "\n"
    
    return acc
