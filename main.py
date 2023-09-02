import requests
import argparse
from dotenv import load_dotenv
import os
import json

def existing_directory(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory '{path}' does not exist")
    return path

def download_course(id, path, endpoint):
    # print(endpoint)
    response = requests.get(endpoint, params={'per_page': 1000})
    # print(response.status_code)
    allFiles = response.json()[0]
    print(json.dumps(allFiles, indent=4))
    
    foldersEndpoint = allFiles['folders_url']
    filesEndpoint = allFiles['files_url']
    # print(foldersEndpoint)
    
    folderResponse = requests.get(foldersEndpoint + "?access_token=" + os.getenv('TOKEN'),
                                  params={'per_page': 1000})
    filesResponse = requests.get(filesEndpoint + "?access_token=" + os.getenv('TOKEN'),
                                 params={'per_page': 1000})
    folders = folderResponse.json()
    files = filesResponse.json()
    print("Carpetas: ")
    print(json.dumps(folders, indent=4))
    print("Archivos fuera de carpetas:")
    print(json.dumps(files, indent=4))
    
    
    
load_dotenv()
TOKEN = os.getenv('TOKEN')
API = "https://canvas.instructure.com/api/v1"
API_COURSES_LIST = API + "/courses?access_token=" + TOKEN
API_COURSES_FILES = API

# TEST = "https://canvas.instructure.com/api/v1/users/89760000000100981/courses"

PARAMS = {
    'include': ['term', 'teachers', 'concluded', 'full_name'],
    'per_page': 1000
}


PATH_TO_DOWNLOAD = './'

# COURSE_NAME = sys.argv[1]

parser = argparse.ArgumentParser(description="Script para descargar archivos de un ramo")

parser.add_argument("sigla", help="Sigla y seccion del curso. Debe estar en mayusculas y \
                                todo junto, de la siguiente manera: IIC2333-1")

parser.add_argument("--output", type=existing_directory, help="Path en donde se descargaran \
                                los archivos. En caso de no ser especificado, se descargaran \
                                en el directorio local")

parser.add_argument("--ayudante", type=bool, help="Busca en los cursos en los que el usuario \
                                es ayudante. Por defecto es False")


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


# print(courses)
for course in courses:
    # print(course['course_code'])
    if args.sigla == course['course_code']:
        number_of_courses += 1
        print("existe el curso!")
        final_course = course
        # print(json.dumps(course, indent=4))     

print("numero de cursos que coinciden: ", number_of_courses)


if number_of_courses == 1:

    API_COURSES_FILES += f"/courses/{final_course['id']}/files?access_token={TOKEN}"
    API_COURSES_FOLDERS = API + f"/courses/{final_course['id']}/folders/by_path?access_token={TOKEN}"
    # API_COURSES_FILES += f"/users/{course['enrollments'][0]['user_id']}/files?access_token={TOKEN}"
    download_course(final_course['id'], PATH_TO_DOWNLOAD, API_COURSES_FOLDERS)
    # print("Curso: ", course)
    
elif number_of_courses == 0:
    print("no existe el curso")
    """print every course available"""
    for course in courses:
        print(course['course_code'])
        
else:
    print("existe mas de un curso con la misma sigla.")      

