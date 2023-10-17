import shutil


def copy_file():
    # Исходный путь к файлу
    source_path = 'ritter_pars.xml'

    # Путь к целевой папке, куда нужно скопировать файл
    destination_folder = '/Users/MacOS/Desktop/Catalog/'

    # Имя файла, каким вы хотите его сохранить в целевой папке
    destination_file_name = 'ritter_pars.xml'

    # Полный путь к целевому файлу
    destination_path = destination_folder + destination_file_name

    # Копирование файла
    shutil.copy(source_path, destination_path)

    print(f"Файл скопирован в {destination_path}")