import reportlab
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from pathlib import Path
import json
import time
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from operator import itemgetter
import json
import pdfkit
from PyPDF2 import PdfFileMerger
import fitz
import shutil









# Insertion of TOC in HTML template.
def collector(arr, file_name):
    if len(arr):
        print(file_name)
        toc_temp = []
        for indx, elemnt in enumerate(arr):
            elem = elemnt['elm']
            page_number = elemnt['page']
            elem = elem.replace('<h1>', '')
            elem = elem.replace('<h2>', '')
            elem = elem.replace('<h3>', '')
            elem = elem.replace('<h4>', '')
            elem = elem.replace('<h5>', '')
            elem = elem.replace('<h6>', '')
            if len(toc_temp) > 0:
                elem_break = elem.split("|")
                if len(elem_break) ==  1:
                    # Other than abstract
                    if elem.strip().lower() == "acknowledgement" or elem.strip().lower() == "acknowledgements" or elem.strip().lower() == "references" or elem.strip().lower() == "reference":
                        toc_temp.append({"index" : 0, "title":elem.strip(), "page": page_number})
                else:
                    # Number Titles
                    title_index = elem_break[0]
                    title = elem_break[1]
                    #print("Hello", elem_break)
                    if str(title_index.strip()).isdecimal() or isfloat(title_index.strip()):
                        print("INDEX TOOK ", title_index)
                        toc_temp.append({"index" : title_index, "title":title.strip(), "page": page_number})
            else:
                res = checkAbstract(elem, indx, page_number, toc_temp)
                if res['result']:
                    toc_temp = res['toc_temp']
        print("JSON", toc_temp)
        colour = ["red", "red", "green", "yellow"]
        with open(file_name + '.html', 'w') as myFile:
            myFile.write('<html>')
            myFile.write("""
                        <head><style>
                                .list li {
                                    position:relative;
                                    overflow:hidden;
                                    width:80%;
                                }

                                .list li:after {
                                    font-family: Times New Roman;
                                    font-size: 60%;
                                    content:"..........................................................................................................................................................................";
                                    text-indent: -1px;
                                    display:block;
                                    letter-spacing:2px;
                                    position:absolute;
                                    left:0px;
                                    bottom:0px;
                                    z-index:-1;
                                    font-weight:bold;
                                }
                                .list li span {
                                    display:inline-block;
                                    background-color:#FFF;
                                    padding-right:5px;
                                }

                                .list li .number {
                                    float:right;
                                    font-weight:bold;
                                    padding-left:5px;
                                }
                                .intender::after{
                                    left: 40px !important;
                                }
                        </style></head>
                """)
            myFile.write('<body>')
            myFile.write("""
                    <div style="margin:25px 22px 200px 22px;">
                     <div style="text-align:center;font-size:150%;letter-spacing:.1em;margin-bottom:10px;margin-right:-.1em;">CONTENTS</div>
                    <ul class="list" style="padding-left:10%;">""")
            

            for title_ele in toc_temp:
                if title_ele['index'] == 0:
                    myFile.write('<li style="margin:0 0 .6em 0;"><span>%4s</span><span class="number">%4d</span></li>' % (str(title_ele['title']).upper(), title_ele['page']));
                else:
                    if "." not in title_ele['index']:
                        myFile.write('<li style="margin:0 0 .5em 0;"><span style="padding-left:.6em;">%4s. %4s</span><span class="number">%4d</span></li>' % (str(title_ele['index']), str(title_ele['title']).upper(), title_ele['page']))
                    else:
                        myFile.write('<li style="margin:0 0 .5em 0;" class="intender"><span style="padding-left:.6em;margin-left: 15px;">%4s. %4s</span><span class="number">%4d</span></li>' % (str(title_ele['index']), str(title_ele['title']).upper(), title_ele['page']))
               


            myFile.write(""" 
                   </ul>
                </div>
                """)
            myFile.write('</body>')
            myFile.write('</html>')
        time.sleep(1)
        
        


      

            
# Specific checking for "Abstract" section to pin the algorithm, after this main content starts. 
def checkAbstract(elem, indx, page_number, toc_temp):
    if "abstract" in elem.lower():
        toc_temp.append({"index" : 0, "title":elem.strip(), "page": page_number})
        return {"result": True, "toc_temp": toc_temp}
    else:
        return {"result": False}







def is_whole(n):
    return n % 1 == 0








# Scraping the HTML from pdf file and tweaking it for efficient output of TOC.
def fileHandler(new_path, file_name, paper_index):
    document = new_path
    doc = fitz.open(document)
    font_counts, styles = fonts(doc, granularity=False)
    size_tag = font_tags(font_counts, styles)
    elements = headers_para(doc, size_tag)
    temp_arr = []
    take_h4 = False
    take_h5 = False
    take_h6 = False
    for indx, elment in enumerate(elements):
        elm = elment['block_string']
        if "abstract" in elm.lower() and "h4" in elm.lower():
            take_h4 = True
        if "abstract" in elm.lower() and "h5" in elm.lower():
            take_h5 = True
        if "abstract" in elm.lower() and "h6" in elm.lower():
            take_h6 = True

        # Header variation handling.
        if "<h1>" in elm or "<h2>" in elm or "<h3>" in elm or "<h4>" in elm or "<h5>" in elm or "<h6>" in elm:
            if take_h6:
                if "<h1>" in elm or "<h2>" in elm or "<h3>" in elm or "<h4>" in elm or "<h5>" in elm or "<h6>" in elm: 
                    if elm[-1] == '|':
                        elm = elm[:-1]
                    temp_arr.append({'page': elment['page'], 'elm': elm})  
            elif take_h5:
                if "<h1>" in elm or "<h2>" in elm or "<h3>" in elm or "<h4>" in elm or "<h5>" in elm:
                    if elm[-1] == '|':
                        elm = elm[:-1]
                    temp_arr.append({'page': elment['page'], 'elm': elm})   
            elif take_h4:
                    if "<h1>" in elm or "<h2>" in elm or "<h3>" in elm or "<h4>" in elm:
                        if elm[-1] == '|':
                            elm = elm[:-1]
                        temp_arr.append({'page': elment['page'], 'elm': elm})
            else:
                if "<h1>" in elm or "<h2>" in elm or "<h3>" in elm:
                    if elm[-1] == '|':
                        elm = elm[:-1]
                    temp_arr.append({'page': elment['page'], 'elm': elm})   

    time.sleep(0.1)
    collector(temp_arr, file_name)
            







# Getting fonts of PDF.
def fonts(doc, granularity=False):
    styles = {}
    font_counts = {}
    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1
    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)
    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")
    
    return font_counts, styles







# Getting font_tags of PDF.
def font_tags(font_counts, styles):
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag







# Getting headers of PDF, also getting on which page number it exists for TOC.
def headers_para(doc, size_tag):
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span
    for indx, page in enumerate(doc):
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append({"page": indx + 1, "block_string": block_string})
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s
                    block_string += "|"
                header_para.append({"page": indx + 1, "block_string": block_string})
    return header_para





def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False



if __name__ == "__main__":
    pass
    import sys,os
    edbt_file_path = Path("edbt.json") # Using edbt.json file already created, availabe in untracked file.
    if edbt_file_path.exists():
        edbt_file = open(edbt_file_path,)
        edbt_file_json = json.load(edbt_file)
        edbt_file.close()
        print("---------------- File edbt.json exists, adding TOC to " + str(len(edbt_file_json)) + " papers .... ----------------")
        time.sleep(4)
        paper_index = 1;
       
        for paper in edbt_file_json: # For each paper
            paper_file_name = paper['path']['$t'].split("/")[1]
            paper_path = "paper_with_pagenumbers/" + paper_file_name
            #if paper_file_name == 'p49.pdf':
            fileHandler(paper_path, paper_file_name, paper_index)
            time.sleep(0.1)
            paper_index += 1
        shutil.copy('images/noimg.png', './') # Copying image to buffer space, needed for final index website.
    else:
        print("---------------- File edbt.json does not exist, restart the process! ----------------")