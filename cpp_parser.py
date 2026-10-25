# Turn cpp files into our 'objects' in python, 1 line at a time
from h_parser import parse_header
from pathlib import Path

class CppVariable:
    def __init__(self, variable_name: str, variable_type: str, variable_value):
        self.name = variable_name
        self.type = variable_type
        self.value = variable_value

    def __init__(self, variable_name: str, variable_type: str):
        self.__init__(variable_name, variable_type, None)

class CppMethod:
    def __init__(self, method_name: str, return_type: str, is_public: bool):
        self.name = method_name
        self.public = is_public
        self.returnType = return_type
        self.instructions = [] # code that runs in order
        self.args = [] # paramaters
        self.variables = [] # CppVariables

    def __len__(self):
        return len(self.instructions)

    def declare_variable(self, new_variable: CppVariable):
        # cpp where u can't double declare variables (scope don't count)
        for var in self.variables:
            if var.name == new_variable.name:
                raise SyntaxError("variable `"+new_variable.name+"` already exists.")
        
        self.variables.append( new_variable )

    # just changes value, doesn't check if the type to change is correct
    def set_variable(self, variable_to_change: CppVariable, new_value):
        for i, val in enumerate(self.variables):
            if val.name == variable_to_change.name:
                self.variables[i].value = new_value
                break
        raise SyntaxError("variable `"+variable_to_change.name+"` was not found inside of the method `"+self.name+"()`.")
        
    def add_arg(self, new_argument_variable):
        self.args.append( new_argument_variable )

    def get_args(self):
        return self.args

    def get_instructions(self):
        return self.instructions

    # TODO: def add_instruction(self, instruction):

class CppClass:
    def __init__(self, class_name: str):
        self.name = class_name
        self.methods = []
        self.variables = []
        self.public_method_indexes = []
        self.public_variables_indexes = []

    # delcare a new method
    def declare_method(self, new_method: CppMethod):
        for func in self.methods:
            if func.name == new_method.name:
                raise SyntaxError("method `"+new_method.name+"()` already exists in class `"+self.name+"`.")

        self.methods.append( new_method )
        if new_method.public:
            self.public_method_indexes.append( len(self.methods)-1 )

    # get ALL methods
    def get_methods(self):
        return self.methods

    # get all PUBLIC methods
    def get_public_methods(self):
        public_methods = []
        for index in self.public_method_indexes:
            public_methods.append( self.methods[index] )
        return public_methods

    def declare_variable(self, new_variable: CppVariable, is_public: bool):
        # cpp where u can't double declare variables (scope don't count)
        for var in self.variables:
            if var.name == new_variable.name:
                raise SyntaxError("variable `"+new_variable.name+"` already exists in class `"+self.name+"`.")
        
        self.variables.append( new_variable )
        if is_public:
            self.public_variables_indexes.append( len(self.variables)-1 )

    # get ALL variables
    def get_variables(self):
        return self.variables

    # get all PUBLIC variables
    def get_public_variables(self):
        public_variables = []
        for index in self.public_variables_indexes:
            public_variables.append( self.variables[index] )
        return public_variables 
        
    # just changes value, doesn't check if the type to change is correct
    def set_variable(self, variable_to_change: CppVariable, new_value):
        for i, val in enumerate(self.variables):
            if val.name == variable_to_change.name:
                self.variables[i].value = new_value
                break
        raise SyntaxError("variable `"+variable_to_change.name+"` was not found inside of class `"+self.name+"`.")  

class Cpp:
    def __init__(self, filename: str):
        self.filename = filename
        self.dependencies = [] # includes
        self.methods = []
        self.variables = []
        self.classes = []
        self.macros = {} # the #define NAME things
        self.instructions = [] # code that runs in order

    def declare_dependency(self, new_depend):
        if new_depend in self.dependencies:
            raise SyntaxError("Dependency `"+new_depend+"` already included")
        self.dependencies.append(new_depend)

    def declare_class(self, new_class: CppClass):
        for clss in self.classes:
            if clss.name == new_class.name:
                raise SyntaxError("class `"+new_class.name+"` already exists in `"+self.filename+"`.")
        self.classes.append( new_class )

    def declare_variable(self, new_variable: CppVariable, is_public: bool):
        for var in self.variables:
            if var.name == new_variable.name:
                raise SyntaxError("variable `"+new_variable.name+"` already exists in `"+self.filename+"`.")
        self.variables.append( new_variable )

    def declare_method(self, new_method: CppMethod):
            for func in self.methods:
                if func.name == new_method.name:
                    raise SyntaxError("method `"+new_method.name+"()` already exists exists in `"+self.filename+"`.")
            self.methods.append( new_method )

def adapt_from_header(header_filepath, cpp_object: Cpp):
    entire_header = parse_header(header_filepath)
    # apply dependencies
    for dep in entire_header.dependencies:
        cpp_object.declare_dependency(dep)

    # declare classes
    for clss in entire_header.classes:
        for existing_class in cpp_object.classes:
            if clss.name == existing_class.name:
                raise SyntaxError("class `"+clss.name+"` already exists in `"+cpp_object.filename+"`.") 

        new_class = CppClass(clss.name)
        for vr in clss.vars:
            new_class.declare_variable( CppVariable(vr.name, vr.type), vr.publicity )
        for meth in clss.methods:
            new_method = CppMethod(meth.name, meth.returnType, meth.isPublic)
            for arg in meth.args:
                new_method.append( arg )
            new_class.declare_method( new_method )
        cpp_object.declare_class( new_class )

    # declare variables
    for var in entire_header.variables:
        cpp_object.declare_variable( CppVariable(var.name, var.type), vr.is_public)

    # declare methods
    for meth in entire_header.methods:
        new_method = CppMethod(meth.name, meth.returnType, meth.isPublic)
        for arg in meth.args:
            new_method.append( arg )
        cpp_object.declare_method( new_method )

    return cpp_object


# syntax_arguments = {"#include": 1}
known_return_types = {"void", "int", "std::string", "float", "char", "long"}



def read_cpp(filepath):
    temp_path = Path(filepath)
    ourcpp = Cpp(temp_path.name)
    code = []
    context = "cpp"
    current_context = ourcpp

    with open(filepath, "r") as file:
        code = file.readlines()

    for raw_line in code:
        stripped_line = raw_line.strip()
        line = stripped_line.split()

        if len(line) == 0: continue # empty line; skip
        if line[0][0:2] == "//": continue # comment line; skip
        if line[0] == "#include":
            ourcpp.declare_dependency(line[1])
            if line[1][0] == '<':
                print("Add Library "+line[1]) # add library
                continue
            elif line[1][-3:-1] == ".h":
                adapt_from_header(filepath+line[1][1:-1], ourcpp) # add header items
                continue
            else:
                print("Add unknown dependency") # probably add a cpp, cannot support at this time
                continue
        if line[0] == "using": continue # namespace most likely, cant support at this time

        # not empty, or comment, or import/include, or namespace

        if line[0] in known_return_types:
            # we're declaring something, get context and understand if its a method or var
            if "(" in line[1]:
                # Method
                endofname = line[1].find("(") # index
                beginningofname = 0
                tempfind = line[1].find("::")
                if tempfind != -1:
                    # declaration from header or earlier context
                    beginningofname = tempfind+2
                method_name = line[1][beginningofname:endofname]
                does_method_already_exist = False
                for i,v in enumerate(current_context.methods):
                    if v.name == method_name:
                        # we found an existing method, skip line bc we have arguments, get code inside
                        does_method_already_exist = True
                        break
                if does_method_already_exist == False:
                    current_context.declare_method(  ) # lets say false by default
            else:
                # Variable
                variable_name = ""
                variable_value = 0
                if "=" in line[1]:
                    variable_name = line[1][0:variable_name.find("=")]
                    if line[1][-1] == "=":
                        # 'type variable_name= value'
                        variable_value = line[2]
                    else:
                        # 'type variable_name=value'
                        variable_value = line[1][ (line[1].find("=")+1): ]
                new_variable = CppVariable(variable_name, line[0])
                new_variable.value = variable_value
                current_context.declare_variable( CppVariable(variable_name, line[0]), False )

        # for item in line:

        





        # try:
        #     cpp_object.declare_dependency(dep)
        # except SyntaxError as e: # dependency already exists
        #     # TODO: Inbuilt console, return e
        #     print(e)
        