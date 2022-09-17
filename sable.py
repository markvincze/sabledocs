import json

class MessageField:
    def __init__(self):
        self.name = ''
        self.label = ''
        self.description = ''
        self.type = ''
        self.full_type = ''
        self.default_value = ''

class Message:
    def __init__(self):
        self.a = ''

class Package:
    def __init__(self):
        self.name = ''
        self.description = ''


# proto_data = ''

with open('description.json') as proto_json_file:
    proto_data = json.load(proto_json_file)

for file in proto_data['files']:
    print(file['package'])

p = Package()
p.name = 'foo'
p.description = 'bar'
print(p.description)
print(p.name)
