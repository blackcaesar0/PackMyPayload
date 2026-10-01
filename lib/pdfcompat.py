#!/usr/bin/python3
#
# Compatibility layer over pypdf / PyPDF2.
#
# PyPDF2 stopped at 3.0.1 and was renamed to pypdf, which dropped every
# camelCase alias (createStringObject, addBlankPage, addJS, addAttachment,
# appendPagesFromReader, numPages, setData...). PackMyPayload used those names
# exclusively, so it could not run against pypdf at all.
#
# pypdf is preferred. PyPDF2 3.x is accepted as a fallback because its
# snake_case API is identical, which lets the rest of the codebase speak one
# dialect regardless of which package is installed.
#

PDF_BACKEND = None

try:
    import pypdf as _pdf
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import (
        ArrayObject,
        DecodedStreamObject,
        DictionaryObject,
        NameObject,
        create_string_object,
    )

    PDF_BACKEND = 'pypdf'

except ImportError:
    try:
        import PyPDF2 as _pdf
        from PyPDF2 import PdfReader, PdfWriter
        from PyPDF2.generic import (
            ArrayObject,
            DecodedStreamObject,
            DictionaryObject,
            NameObject,
        )

        try:
            from PyPDF2.generic import create_string_object
        except ImportError:                      # PyPDF2 < 2.x
            from PyPDF2.generic import createStringObject as create_string_object

        PDF_BACKEND = 'PyPDF2'

    except ImportError:
        _pdf = None


def available():
    return PDF_BACKEND is not None


def backend_version():
    if _pdf is None:
        return None
    return f'{PDF_BACKEND} {getattr(_pdf, "__version__", "unknown")}'


def require():
    '''Raise a MissingDependency-style error when no PDF backend is installed.'''

    if _pdf is None:
        from lib.deps import MissingDependency
        raise MissingDependency('pdf', 'pypdf', 'pypdf')


def stream_set_data(stream, data):
    '''DecodedStreamObject.set_data(), tolerating the old camelCase name.'''

    if hasattr(stream, 'set_data'):
        stream.set_data(data)
    else:
        stream.setData(data)


def writer_blank_page(writer, width, height):
    if hasattr(writer, 'add_blank_page'):
        return writer.add_blank_page(width = width, height = height)
    return writer.addBlankPage(width = width, height = height)


def writer_add_js(writer, js):
    if hasattr(writer, 'add_js'):
        return writer.add_js(js)
    return writer.addJS(js)


def writer_add_attachment(writer, name, data):
    if hasattr(writer, 'add_attachment'):
        return writer.add_attachment(name, data)
    return writer.addAttachment(name, data)


def writer_append_pages(writer, reader):
    if hasattr(writer, 'append_pages_from_reader'):
        return writer.append_pages_from_reader(reader)
    return writer.appendPagesFromReader(reader)


def reader_num_pages(reader):
    try:
        return len(reader.pages)
    except Exception:
        return reader.numPages


def writer_root(writer):
    '''The writer's document catalog, named differently across versions.'''

    for attr in ('_root_object', 'root_object'):
        if hasattr(writer, attr):
            return getattr(writer, attr)

    raise AttributeError('Could not locate PDF writer root object')
