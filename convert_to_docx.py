import pypandoc

try:
    pypandoc.get_pandoc_version()
except OSError:
    print("Pandoc not found. Downloading...")
    pypandoc.download_pandoc()

print("Converting to DOCX...")
pypandoc.convert_file("FINAL_PROJECT_IMPLEMENTATION.md", "docx", outputfile="FINAL_PROJECT_IMPLEMENTATION.docx")
print("Conversion complete.")
