class BadFile(Exception):
    pass

from contextlib import contextmanager

@contextmanager
def file_handler(file, mode):
    resource = open(file, mode)
    try:
        print("file accessed successfully")
        yield resource
    finally:
        print("file resource released\n")
        resource.close()

try:
    with file_handler("20220126_premarketCorpPfdLamrCorporateActionsV2.cax", "r"):
        raise BadFile
except:
    print("something went wrong")
