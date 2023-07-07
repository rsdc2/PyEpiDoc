from pyepidoc.epidoc import scripts

def tokenize_file():

    scripts.tokenize(
        src_folderpath='/home/robert/Documents/programming/crossreads/texts/ISicily-live/ISicily/inscriptions',
        dst_folderpath='/home/robert/Documents/programming/python/crossreads/pyepidoc/PyEpiDoc/data/isicily_tokenized_with_ids',
        isic_ids=['ISic000002'],
        space_words=True,
        set_ids=True,
        fullpath=True
    )

def tokenize_files():
    ids = [
        'ISic003364', 
        'ISic020602', 
        'ISic020603', 
        'ISic020600', 
        'ISic030303', 
        'ISic030319', 
        'ISic001420', 
        'ISic001473', 
        'ISic020288',
        'ISic020292',
        'ISic020298', 
        'ISic020300',
        'ISic020304',
        'ISic020306', 
        'ISic020317', 
        'ISic020319',
        'ISic020313', 
        'ISic020320',
        'ISic020322',
        'ISic020323',
        'ISic020368',
        'ISic020370',
        'ISic020371',
        'ISic001447',
        'ISic001445',
        'ISic001448',
        'ISic001473', 
        'ISic001463', 
        'ISic001464', 
        'ISic001465', 
        'ISic001466', 
        'ISic001467', 
        'ISic001468',
        'ISic001469', 
        'ISic001470',
        'ISic001568',
        'ISic001408',
        'ISic001439', 
        'ISic001471', 
        'ISic001472', 
        'ISic001474', 
        'ISic001478', 
        'ISic001481', 
        'ISic001483', 
        'ISic001488', 
        'ISic003107', 
        'ISic003363', 
        'ISic003375', 
        'ISic003474', 
        'ISic020445', 
        'ISic020598', 
        'ISic020597', 
        'ISic001485', 
        'ISic020930', 
        'ISic001435' ]

    scripts.tokenize(
        src_folderpath='/home/robert/Documents/programming/crossreads/texts/ISicily-live/ISicily/inscriptions',
        dst_folderpath='/home/robert/Documents/programming/python/crossreads/pyepidoc/PyEpiDoc/data/isicily_tokenized_with_ids',
        isic_ids=ids,
        space_words=True,
        set_ids=False,
        fullpath=True
    )

tokenize_files()