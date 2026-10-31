"""Use the packaged DOCX rasterizer with a native Microsoft Word PDF conversion.
Windows bundle has no LibreOffice; never falls back to a desktop LibreOffice install.
"""
import functools
import importlib.util
from pathlib import Path
import sys
from pdf2image import convert_from_path
renderer=Path(r'C:\Users\amitk\.codex\plugins\cache\openai-primary-runtime\documents\26.1026.10807\skills\documents\render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',renderer)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
docx,pdf,output=map(lambda x:str(Path(x).resolve()),sys.argv[1:4])
assert Path(pdf).is_file()
module.convert_to_pdf=lambda *args,**kwargs:(pdf,'Native Microsoft Word ExportAsFixedFormat; existing DOCX unchanged except fields')
module.convert_from_path=functools.partial(convert_from_path,poppler_path=r'C:\Users\amitk\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin')
pages=module.rasterize(docx,output,dpi=130,verbose=True,emit_pdf=False)
print('Rendered',len(pages),'pages')
