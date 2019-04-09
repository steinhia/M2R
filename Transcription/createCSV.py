import tgt
import csv

with open('essai.csv', mode='w') as f:
    csv_w = csv.writer(f, delimiter=',')
    csv_w.writerow(['nom_fichier','transcription','traduction','commentaires',0,0])
    TG=tgt.io.read_textgrid('essai.txtGrid', include_empty_intervals=False)
    Tier=TG.get_tier_by_name('transcription')
    for i in Tier:
        csv_w.writerow(['nom','','','',i.start_time,i.end_time])

