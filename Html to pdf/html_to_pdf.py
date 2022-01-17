from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from os import listdir

mypath = '/Users/rustamwho/Downloads/book/'  # here path to all .html files
filenames = [f for f in listdir(mypath) if '.html' in f]
files_count = len(filenames)

for i, filename in enumerate(filenames):
    print(f'Current file: {filename}')
    drawing = svg2rlg(mypath + filename)
    renderPDF.drawToFile(drawing, mypath + 'pdf/' + filename[:-5] + '.pdf')
    print(f'Rendered files: {i} from {files_count}')
