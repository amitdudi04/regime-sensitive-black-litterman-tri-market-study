import sys
import os

print("Exporting Word Document to PDF format utilizing comtypes (Windows Native)...")
try:
    import comtypes.client
    
    # Needs absolute paths for Word COM iteration
    in_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'docs', 'FINAL_RESEARCH_RESULTS_COMPENDIUM.docx'))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'docs', 'FINAL_RESEARCH_RESULTS_COMPENDIUM.pdf'))
    
    word = comtypes.client.CreateObject('Word.Application')
    doc = word.Documents.Open(in_file)
    doc.SaveAs(out_file, FileFormat=17) # 17 = wdFormatPDF
    doc.Close()
    word.Quit()
    print(f"Successfully generated: {out_file}")
except Exception as e:
    print(f"Error executing COM Client conversion: {str(e)}")
    print("Fallback: Academic reviewer to export PDF directly from MS Word.")
