from .models import CodeSnippets, Media


def is_valid_file(file, max_size=10000000) -> bool:
    """
    Author : Pavan
    Params : file object and maximum size of the file
    Returns : returns true if file size is less than 10MB else false.
    Created On : 12-10-2024
    """
    return len(file) <= max_size


def add_codes(request, blog):
    """
    Author : Pavan
    Params : request object, blog object
    Returns : returns number of codes updated, created and their description
    Created On : 12-10-2024
    """
    code_blocks = request.data.get("code_snippets", None)
    if code_blocks is None:
        code_blocks = []
        snippets_added = 0
        snippets_updated = 0
        code_files = []
    for code_description in code_blocks:
        code = code_blocks[code_description]
        count = CodeSnippets.objects.filter(
            code_description=code_description, blog_id=blog
        ).update(code_content=code)
        if count == 1:
            snippets_updated = snippets_updated + 1
        else:
            snippets_added = snippets_added + 1
            code_snippets = CodeSnippets.objects.create(
                code_description=code_description,
                blog_id=blog,
                code_content=code,
            )
            code_snippets.save()
        code_files.append(code_description)
    return {
        "snippets_added": snippets_added,
        "snippets_updated": snippets_updated,
        "snippets": code_files,
    }


def save_files(request, blog):
    """
    Author : Pavan
    Params : request object, blog object
    Returns : returns media file names if created or updated.
    Created On : 12-10-2024
    """
    media_files = []
    for file in request.FILES:
        file_data = request.FILES[file]
        if is_valid_file(file_data):
            binary_file = file_data.read()
            count = Media.objects.filter(
                media_name=file_data.name, blog_id=blog
            ).update(media=binary_file)
            if count == 1:
                media_files.append(file_data.name)
            else:
                media = Media.objects.create(
                    media=binary_file, media_name=file_data.name, blog_id=blog
                )
                media.save()

    media_files.append(media.media_name)
    return media_files
