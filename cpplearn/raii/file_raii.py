class BadFile(Exception):
    pass


from contextlib import contextmanager


@contextmanager
def file_handler(file, mode):
    try:
        print(f"file resource: {file} acquired")
        resource = open(file, mode)
    except OSError:
        raise BadFile(f"{file} failed to be opened")
    try:
        yield resource
    finally:
        print("file resource released\n")
        resource.close()


try:
    with file_handler("test.txt", "w+") as f:
        for i in range(3):
            f.write("Hello RAII")
            print("file accessed successfully")
except:
    print("something went wrong")
