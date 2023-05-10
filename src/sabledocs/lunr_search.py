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

    # documents = [{
    #          "package": "postsaleapi",
    #          "content": """Mr. Green killed Colonel Mustard in the study with the
    #  candlestick. Mr. Green is not a very nice fellow.""",
    #          "url": "/google.datastore.v1.html"
    #      }, {
    #          "package": "baggagehub",
    #          "content": "Professor Plumb has a green and a yellow plant in his study",
    #          "url": "/google.pubsub.v1.html"
    #      }, {
    #          "package": "seathub",
    #          "content": """Miss Scarlett watered Professor Plumbs green plant
    #  while he was away on his murdering holiday.""",
    #          "url": "/google.datastore.v1.html"
    #      }]

    builder = lunr.get_default_builder()
    builder.metadata_whitelist.append("position")
    # builder.

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
    acc += service.full_name + "\n"
    acc += service.description + "\n"
    for method in service.methods:
        acc += method.name + "\n"
        acc += method.description + "\n"
        acc += method.request.full_type + "\n"
        acc += method.response.full_type + "\n"
    
    return acc


def append_message_content(acc: str, message: Message):
    acc += message.full_name + "\n"
    acc += message.description + "\n"
    for field in message.fields:
        acc += field.name + "\n"
        acc += field.description + "\n"
    
    return acc


def append_enum_content(acc: str, enum: Enum):
    acc += enum.full_name + "\n"
    acc += enum.description + "\n"
    for value in enum.values:
        acc += value.name + "\n"
        acc += value.description + "\n"
    
    return acc
