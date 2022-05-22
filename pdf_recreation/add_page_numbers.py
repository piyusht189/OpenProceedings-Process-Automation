import reportlab
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from pathlib import Path
import json
import time
from PyPDF2 import PdfFileWriter, PdfFileReader
tmp = "__tmp.pdf"



# Function to only process page number text (styling it using canvas) and exporting it as a layer.
def createPagePdf(num, tmp):
    c = canvas.Canvas(tmp)
    for i in range(1,num+1): 
        c.setFont("Helvetica", 8) 
        c.drawString((210//2)*mm, (5)*mm, str(i))
        c.showPage()
    c.save()
    return 
    with open(tmp, 'rb') as f:
        pdf = PdfFileReader(f, strict=False)
        layer = pdf.getPage(0)
    return layer



# Using PDFFileWriter to add styled page number layer at the  bottom of the pdf (Paper) & storing it.
def fileHandler(path, file_name, i):
    batch = 10
    batch = 0
    output = PdfFileWriter()
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f,strict=False)
        n = pdf.getNumPages() # Gets the number of pages in that pdf.
        if batch == 0:
            batch = -n
        createPagePdf(n,tmp)
        if not os.path.isdir('paper_with_pagenumbers/'):
            os.mkdir('paper_with_pagenumbers/')
        with open(tmp, 'rb') as ftmp:
            numberPdf = PdfFileReader(ftmp, strict=False)
            print("Adding Page Numbers to paper index " + str(i) + " ====> " + file_name)
            for p in range(n):
                if not p%batch and p:
                    newpath = 'paper_with_pagenumbers/' + file_name
                    with open(newpath, 'wb') as f:
                        output.write(f)
                    output = PdfFileWriter()
#                sys.stdout.write('\rpage: %d of %d'%(p, n))
                
                page = pdf.getPage(p)
                numberLayer = numberPdf.getPage(p)
                
                page.mergePage(numberLayer)
                output.addPage(page)
            if output.getNumPages():
                newpath = 'paper_with_pagenumbers/' + file_name
                with open(newpath, 'wb') as f:
                    output.write(f)
    
        os.remove(tmp)


# Main execution starts
if __name__ == "__main__":
    pass
    import sys,os

    edbt_file_path = Path("edbt.json") # Using edbt.json file already created, availabe in untracked file.
    if edbt_file_path.exists():
        edbt_file = open(edbt_file_path,)
        edbt_file_json = json.load(edbt_file)
        edbt_file.close()
        print("---------------- File edbt.json exists, adding page numbers to " + str(len(edbt_file_json)) + " papers .... ----------------")
        paper_index = 1;
        for paper in edbt_file_json: # Iterating through each paper.
            paper_path = "main_data/proceedings/" + paper['path']['$t'];
            paper_file_name = paper['path']['$t'].split("/")[1];
            fileHandler(paper_path, paper_file_name, paper_index)
            time.sleep(0.1)
            paper_index += 1

    else:
        print("---------------- File edbt.json does not exist, restart the process! ----------------")

   
    exit()

    