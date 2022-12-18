from setuptools import find_packages,setup

from typing import List



REQUIREMENT_FILE_NAME = "requirements.txt"
HYPHEN_E_DOT = "-e ."                                       ## "-e ." means editable installation, it means we are writing our code and we can modeify our code and we can install it,,,, "." denotes current directry{our sensor folder containing sourcecode is our current directory, and it is pointing towrds that sensor folder },,,,,keeping "-e ." inside requirement.txt file so that when we install whatever mentioned inside requirements.txt by running pip install -r requirements.txt{basically this command "pip install -r requirements.txt" install after reading whatever inside the .txt file}, then this "-e ." present inside it will trigger the setup.py file, i.e.,the setup of our project, i.e., it will install the sensor folder{which contains our project's source code} as a package like other packages present inside the requirements.txt file,,,,,,,,,but while mentioning the list of the things to be installed inside the "install_requires" parameter this"-e ." will also be present inside the list of the things to be installed, and we will not be needing it so we will try to remove it insdie the below function, and to do that we are assigning this to a variable which we will to refer to this "-e .".

def get_requirements():                                     ##this function will return list of strings{the libraries that we have mentioned inside requirement.txt file}
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
    requirement_list=[requirement_name.replace("\n","") for requirement_name in requirement_list]    ##as in the list in the requirements.txt this"\n" is not visible but it is there which will come in the list we going to create so we replaced it with nothing while creating the list of the libraries to be installed
    if HYPHEN_E_DOT in requirement_list:
        requirement_list.remove(HYPHEN_E_DOT)
    return requirement_list




##in this setup function, specify version and other details 
setup(
    name ="sensor",
    version ="0.0.1",                                       ##as this is the first time code being written for this project, hence this is the first version ,,, so everytime chanages made to the sorcecode, new version is produced
    author="Rajesh",
    author_email="rajesh29049495@gmail.com",
    packages= find_packages(),                              ##this will find those folders with code,,, suppose i created a sensor folder in which i put all the files with code, now when this setup function is run then this find_packages parameter will consider that sensor folde as a package and its code containing .py files as modules, and it is able to find it because we have put a specific file "__init__.py" in the sensor folder
    install_requires= get_requirements()                    ##this "get_requirements" function will give list of the packages we will install during the project 
)