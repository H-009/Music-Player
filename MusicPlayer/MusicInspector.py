import os

class Inspector:

    @staticmethod
    def is_folder_empty(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                return False
        return True