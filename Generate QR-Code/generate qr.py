import qrcode
# still need install a Pillow

name = 'IFS final Rus'
vcard_file_name = name+'.vcf'
with open(vcard_file_name,encoding='utf-8') as myfile:
    vcard = myfile.read()

img = qrcode.make(vcard)
img.save(f'{name}.png', 'PNG', optimize=True)
