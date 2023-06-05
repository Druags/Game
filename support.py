from os import walk


def import_folder(path):
    surface_list = []

    for _, _, image_files in walk(path):
        for image in image_files:
            print(image)
    return surface_list