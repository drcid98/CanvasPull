import requests
import argparse
from dotenv import load_dotenv
import os
import json


def existing_directory(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory '{path}' does not exist")
    return path


def folder_exists(path):
    if not os.path.isdir(path):
        return False
    return True


def file_exists(path):
    if not os.path.isfile(path):
        return False
    return True


# Esta sirve para cuando ponga un flag o algo en el que permita verificar archivos
# que han sido modificados
def files_are_equal_size(file_1, size_file_2):
    if os.path.getsize(file_1) == size_file_2:
        return True
    return False


def download_files(path, endpoint):
    response = requests.get(endpoint, params={'per_page': 1000})
    allFiles = response.json()
    
    for file in allFiles:
        
        try:
            fileName = file['display_name']
            if not file_exists(os.path.join(path, fileName)):
                    r = requests.get(file['url'], allow_redirects=True)
                    open(os.path.join(path, fileName), 'wb').write(r.content)
        except KeyError:
            foldersEndpoint = file['folders_url']
            filesEndpoint = file['files_url']
            
            folderResponse = requests.get(foldersEndpoint + "?access_token=" + os.getenv('TOKEN'),
                                        params={'per_page': 1000})
            filesResponse = requests.get(filesEndpoint + "?access_token=" + os.getenv('TOKEN'),
                                        params={'per_page': 1000})
            folders = folderResponse.json()
            files = filesResponse.json()

            for folder in folders:
                folderName = folder['name']
                if not folder_exists(os.path.join(path, folderName)):
                    os.mkdir(os.path.join(path, folderName))
                
                numberOfFiles = folder['files_count']
                numberOfFolders = folder['folders_count']
                
                if numberOfFolders != 0:
                    download_files(os.path.join(path, folderName),
                                   folder['folders_url'] + "?access_token=" + os.getenv('TOKEN'))
                
                if numberOfFiles != 0:
                    download_files(os.path.join(path, folderName),
                                   folder['files_url'] + "?access_token=" + os.getenv('TOKEN') )

            for file in files:
                fileName = file['display_name']
                if not file_exists(os.path.join(path, fileName)):
                    r = requests.get(file['url'], allow_redirects=True)
                    open(os.path.join(path, fileName), 'wb').write(r.content)
                

load_dotenv()
TOKEN = os.getenv('TOKEN')
API = "https://canvas.instructure.com/api/v1"
API_COURSES_LIST = API + "/courses?access_token=" + TOKEN
API_COURSES_FILES = API

PARAMS = {
    'include': ['term', 'teachers', 'concluded', 'full_name'],
    'per_page': 1000
}


PATH_TO_DOWNLOAD = './'

parser = argparse.ArgumentParser(description="Script para descargar archivos de un ramo")

parser.add_argument("sigla", help="Sigla y seccion del curso. Debe estar en mayusculas y \
                                todo junto, de la siguiente manera: IIC2333-1")

parser.add_argument("--output", type=existing_directory, help="Path relativo en donde se descargaran \
                                los archivos. En caso de no ser especificado, se descargaran \
                                en el directorio local")

parser.add_argument("--ayudante", type=bool, help="Busca en los cursos en los que el usuario \
                                es ayudante. Por defecto es False. \n ESTA FUNCIONALIDAD NO \
                                ESTA IMPLEMENTADA AUN")


args = parser.parse_args()


if args.output:
    print("Descargando archivos en path: ", args.output)
    PATH_TO_DOWNLOAD = args.output


response = requests.get(API_COURSES_LIST, params=PARAMS)

number_of_courses = 0

if response.status_code != 200:
    print("Error al obtener los cursos")
    print("Codigo de error: ", response.status_code)

courses = response.json()

final_course = ''


for course in courses:
    if args.sigla == course['course_code']:
        number_of_courses += 1
        print("existe el curso!")
        final_course = course

print("numero de cursos que coinciden: ", number_of_courses)


if number_of_courses == 1:

    API_COURSES_FILES += f"/courses/{final_course['id']}/files?access_token={TOKEN}"
    API_COURSES_FOLDERS = API + f"/courses/{final_course['id']}/folders/by_path?access_token={TOKEN}"
    
    download_files(PATH_TO_DOWNLOAD, API_COURSES_FOLDERS)
    
elif number_of_courses == 0:
    print("no existe el curso")
    """print every course available"""
    for course in courses:
        print(course['course_code'])
        
else:
    print("existe mas de un curso con la misma sigla.")      

