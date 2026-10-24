# Turn h files into our 'objects' in python, 1 line at a time

# Argument relation
syntaxTable = {}

class CppHeaderVariable:
    def __init__(self):
        self.name 

class CppHeaderMethod:
    def __init__(self, method_name: str, isPublic: bool, returnType: str):
        self.name = method_name
        self.isPublic = isPublic
        self.returnType = returnType
        self.args = {}

    def add_argument(self, argumentName: str, argumentType: str, argumentIndex: int):
        self.args[argumentName] = {argumentType, argumentIndex}

    def get_arguments(self):
        return self.args


# Header Guards
class CppHeader:
    def __init__(self, header_file_name: str):
        self.filename = header_file_name
        self.id: str = None
        self.dependencies = {}
        self.methods = {}