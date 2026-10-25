# Turn h files into our 'objects' in python, 1 line at a time
# python file will have a method that allows for the input of an actual C/C++ header file, and return a Python 'CppHeader' object filled out from the C/C++ header file.

"""
For Example:

h_parser.parse_header("examples/example_header_1.h")

takes in the file directory of a header file, and the function itself will return a CppHeader
class instance.

example_header_1.h is as follows:

    #pragma once
    #include <string.h>
    using namespace std;

    class login
    {
    private:
        void DrunkGame();
        void DeleteLine(string username);

    public:
        void Login();
        void Registration();
        void ForgotPassword();
    };

our parse_header() method will return:

CppHeader Object:
    filename      = "example_header_1.h"
    id            = "EXAMPLE_HEADER_1_H"
    dependencies  = [ "<string.h>" ]
    methods       = [ ] # empty because all of the methods are delcared INSIDE the class 'login'
    variables     = [ ] # no global vars
    classes       = [
        CppHeaderClass Object:
            ...
            methods = [
                CppHeaderMethod Object:
                    name       = "DrunkGame"
                    isPublic   = False
                    returnType = "void"
                    args       = [ ]
                ,
                CppHeaderMethod Object:
                    name       = "DeleteLine"
                    isPublic   = False
                    returnType = "void"
                    args       = [ (string, "example") ]
                ,
                etc.
        ]
    ]

    gonna return that CppHeader in the parse_header() method
"""

# Argument relation
syntaxTable = {}

# Header File Classes, once again its an interface
class CppHeaderClass:
    def __init__(self, class_name):
        self.name = class_name
        self.vars= []
        self.methods= []
        
        # local vars, local methods, etc.

# Global vars but are interfaces so they're not set
class CppHeaderVariable:
    def __init__(self, variable_name: str, variable_type: str, publicity):
        self.name = variable_name
        self.type = variable_type
        self.publicity= publicity

# Each method inside of a header class, they're interfaces
class CppHeaderMethod:
    def __init__(self, method_name: str, isPublic: bool, returnType: str):
        self.name = method_name
        self.isPublic = isPublic
        self.returnType = returnType
        self.args = []

    def add_argument(self, new_argument_variable: CppHeaderVariable):
        self.args.append( new_argument_variable )

    def get_arguments(self):
        return self.args

# The entire CppHeader Class
class CppHeader:
    def __init__(self, header_file_name: str):
        self.filename = header_file_name
        self.id: str = None
        self.dependencies = []
        self.methods = []
        self.variables = []
        self.classes = []
         
    def declare_method(self,new_method):
        for meth in self.methods:
            if meth.name == new_method.name:
                raise SyntaxError("THAT SIHT ALREADY DELCARED")
        self.methods.append(new_method)
        
    def declare_dependency(self, new_depend):
        if new_depend in self.dependencies:
            raise SyntaxError("Dependency has been declared?")
        self.dependencies.append(new_depend)
        
    def declare_class(self,new_class):
        for clas in self.classes:
            if clas.name == new_class.name:
                raise SyntaxError("Class has already been declared")
        self.classes.append(new_class)

    def declare_variable(self, new_var):
        for variable in self.variables:
            if variable.name == new_var.name:
                raise SyntaxError("variable has already been declared")
        self.variables.append(new_var)

    def set_id(self,id):
        self.id = id; 
    # add the adders for the lists, and a setter for the id



# Classes are done, time to do the ACTUAL parsing part
# Another class will call `parse_header(filepath)` and you'll run an open on this filepath
# you'll read from line to line slowly creating your CppHeader class

#progress so far, seems pretty much finished i think just need maybe id stuff and other minor things like global methods that arent in classes if there are any
def parse_header(filepath, name_of_file):
    with open(filepath, "r") as file:
        mainobj= CppHeader(name_of_file)
        current_class= []
        pub=False
        glob = True
        for line in file:
            line= line.strip()
            copline= line
            line= line.split()
            if "#include" in line:
                mainobj.declare_dependency(line[1])

            elif len(line) ==0:
                continue

            elif "class" not in line and "(" not in line[1] and glob == True:
                varobj= CppHeaderVariable(line[1], line[0], True)
                mainobj.declare_variable(varobj) 

            elif "class" in line:
                classobj= CppHeaderClass(line[1])
                mainobj.declare_class(classobj)
                current_class.append(classobj)
                glob = False

            elif "};" in line:
                current_class.pop()
                glob = True

            elif "private:" in line:
                pub=False

            elif "public:" in line:
                pub = True

            elif "(" not in line[1]:
                if pub == True:
                  varobj= CppHeaderVariable(line[1], line[0], True)
                  current_class[-1].vars.append(varobj)
                else:
                    varobj = CppHeaderVariable(line[1], line[0], False)
                    current_class[-1].vars.append(varobj)

            elif "(" in line[1]:
                if pub ==True:
                  methodobj= CppHeaderMethod(line[1].split("(")[0], True ,line[0])
                  params=copline.split("(")[1].split(")")[0]
                  paramlis= [p.strip() for p in params.split(",")]
                  if paramlis[0] != "":
                    for param in paramlis:
                        param=param.split()
                        varobj= CppHeaderVariable(param[1], param[0],True)
                        methodobj.add_argument(varobj)
                  current_class[-1].methods.append(methodobj)

                else:
                  methodobj= CppHeaderMethod(line[1].split("(")[0], False, line[0])
                  params=copline.split("(")[1].split(")")[0]
                  paramlis= [p.strip() for p in params.split(",")]
                  if paramlis[0] != "":
                    for param in paramlis:
                        param=param.split()
                        varobj = CppHeaderVariable(param[1], param[0],False)
                        methodobj.add_argument(varobj)
                  current_class[-1].methods.append(methodobj)

        # ...


# https://github.com/The-Young-Programmer/C-CPP-Programming/blob/main/Projects/C%2B%2B%20Projects/Basic/A%20Login%20and%20Registration%20System/login.h