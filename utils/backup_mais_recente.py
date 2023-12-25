import os


def last_backup_folder(dir: str) -> str:
    diretorios = [os.path.join(dir, d) for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    return max(diretorios, key=os.path.getmtime)


if __name__ == "__main__":
    print(last_backup_folder("path_to_backup_folder"))
