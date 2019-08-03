

"""
import adb_utils.Pretty_DocString
reload(adb_utils.Pretty_DocString)

from adb_utils.Pretty_DocString import doc_string
"""

# def docString(func):
#   def wrap(*args, **kwargs):
#     print("\n================== DOC STRING ==========================")
#     func(*args, **kwargs)
#     print("=======================================================\n")
#   return wrap

def docString(func):
    """ doc string decorator"""
    def wrap(*args, **kwargs):
        print("\n===========================================================================================")
        print('\nDOC STRING:')
        print('-----------')
        func(*args, **kwargs)    
        print("===========================================================================================\n")
    return wrap


@docString
def doc_string(func):
    print func.__doc__




