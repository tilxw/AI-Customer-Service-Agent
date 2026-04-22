import os

def get_project_root() -> str:
    """获取项目根目录绝对路径。

    实现思路：
    当前文件位于 utils 目录，因此取当前文件目录的上一级即项目根目录。
    """

    #当前文件绝对路径
    current_file = os.path.abspath(__file__)
    #当前文件夹绝对路径
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path: str) -> str:
    """把项目内相对路径转换为绝对路径。"""
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)

if __name__ == '__main__':
    print(get_abs_path("config\config.txt"))
