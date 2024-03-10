import requests
import argparse
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import zipfile
import threading


def existing_directory(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Directory '{path}' does not exist")
    return path

def get_year_semester(date):
    year = date.year
    month = date.month
    if month <= 4:
        return f'{year}-1'
    if month >= 10:
        return f'{year+1}-1'
    return f'{year}-2'

def zip_dir(directory, zip_file):
    """
    Compresses the contents of a directory into a ZIP file.
    
    :param directory: The path to the directory to be compressed.
    :param zip_file: The path to the ZIP file to create.
    """
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))


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

def download_file(url, file_path):
    """
    Downloads a single file from a URL and saves it to the specified file path.
    
    :param url: The URL of the file to download.
    :param file_path: The file path where the file will be saved.
    """
    r = requests.get(url, allow_redirects=True)
    with open(file_path, 'wb') as f:
        f.write(r.content)

def download_files(path, endpoint):
    """
    Downloads files from an API endpoint to the specified path using threading.
    
    :param path: The directory where files will be saved.
    :param endpoint: The API endpoint to retrieve files and folders information.
    """
    response = requests.get(endpoint, params={'per_page': 1000})
    all_files = response.json()
    threads = []
    
    for item in all_files:
        try:
            file_name = item['display_name']
            if not file_exists(os.path.join(path, file_name)):
                file_url = item['url']
                thread = threading.Thread(target=download_file, args=(file_url, os.path.join(path, file_name)))
                thread.start()
                threads.append(thread)
        except KeyError:
            folders_endpoint = item['folders_url']
            files_endpoint = item['files_url']
            folder_response = requests.get(folders_endpoint + "?access_token=" + os.getenv('TOKEN'),
                                            params={'per_page': 1000})
            files_response = requests.get(files_endpoint + "?access_token=" + os.getenv('TOKEN'),
                                           params={'per_page': 1000})
            folders = folder_response.json()
            files = files_response.json()
            
            for folder in folders:
                folder_name = folder['name']
                if not folder_exists(os.path.join(path, folder_name)):
                    os.mkdir(os.path.join(path, folder_name))
                download_files(os.path.join(path, folder_name),
                               folder['folders_url'] + "?access_token=" + os.getenv('TOKEN'))
                download_files(os.path.join(path, folder_name),
                               folder['files_url'] + "?access_token=" + os.getenv('TOKEN'))
            
            for file in files:
                file_name = file['display_name']
                if not file_exists(os.path.join(path, file_name)):
                    file_url = file['url']
                    thread = threading.Thread(target=download_file, args=(file_url, os.path.join(path, file_name)))
                    thread.start()
                    threads.append(thread)
    
    for thread in threads:
        thread.join()

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

parser.add_argument("--todos", type=bool, help="Descarga todos los cursos en los que este el usuario. \
                                Por defecto es False. \n ESTA FUNCIONALIDAD NO \
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
courses.sort(key=lambda x: x['created_at'], reverse=True)
if args.todos:
    print("Descargando todos los cursos")
    PATH_TO_DOWNLOAD = os.path.join(PATH_TO_DOWNLOAD, "descarga")
    if not folder_exists(PATH_TO_DOWNLOAD):
        os.mkdir(PATH_TO_DOWNLOAD)
    for course in courses:
        year_semester = get_year_semester(datetime.strptime(course['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
        print(course['course_code'], year_semester)
        API_COURSES_FILES += f"/courses/{course['id']}/files?access_token={TOKEN}"
        API_COURSES_FOLDERS = API + f"/courses/{course['id']}/folders/by_path?access_token={TOKEN}"
        if not folder_exists(os.path.join(PATH_TO_DOWNLOAD, year_semester)):
            os.mkdir(os.path.join(PATH_TO_DOWNLOAD, year_semester))
        os.mkdir(os.path.join(PATH_TO_DOWNLOAD, year_semester, course['course_code']))
        print("Descargando archivos de ", course['course_code'])
        download_files(os.path.join(PATH_TO_DOWNLOAD, year_semester, course['course_code']), API_COURSES_FOLDERS)
        print("Archivos descargados")
    print("Descarga completa")
    print("Comprimiendo archivos")
    zip_dir(PATH_TO_DOWNLOAD, 'descarga.zip')
    exit()
        

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
        formatted_date = datetime.strptime(course['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        print(course['course_code'], get_year_semester(formatted_date))
        
else:
    print("existe mas de un curso con la misma sigla.")      

