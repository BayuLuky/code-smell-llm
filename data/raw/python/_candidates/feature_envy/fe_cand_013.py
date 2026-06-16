def run(self):
    # Remove c files if we are not within a sdist package
    cwd = os.path.abspath(os.path.dirname(__file__))
    remove_c_files = not os.path.exists(os.path.join(cwd, "PKG-INFO"))
    if remove_c_files:
        print("Will remove generated .c files")
    if os.path.exists("build"):
        shutil.rmtree("build")
    for dirpath, dirnames, filenames in os.walk("sklearn"):
        for filename in filenames:
            root, extension = os.path.splitext(filename)

            if extension in [".so", ".pyd", ".dll", ".pyc"]:
                os.unlink(os.path.join(dirpath, filename))

            if remove_c_files and extension in [".c", ".cpp"]:
                pyx_file = str.replace(filename, extension, ".pyx")
                if os.path.exists(os.path.join(dirpath, pyx_file)):
                    os.unlink(os.path.join(dirpath, filename))

            if remove_c_files and extension == ".tp":
                if os.path.exists(os.path.join(dirpath, root)):
                    os.unlink(os.path.join(dirpath, root))

        for dirname in dirnames:
            if dirname == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, dirname))
