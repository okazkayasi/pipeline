import datetime
import ftplib
import pandas as pd
import gc

d1 = datetime.date(2019, 1, 1)
d2 = datetime.date(2020, 6, 30)
days = [d1 + datetime.timedelta(days=x) for x in range((d2-d1).days + 1)]
filenames = []
for day in days:
    filename = 'aisdk_' + day.strftime('%Y%m%d') + '.csv'
    print(filename)
    filenames.append(filename)

print(filenames)


FTP_HOST = "ftp.ais.dk"
FTP_USER = "anonymous"
FTP_PASS = "okazkayasi@outlook.com"

ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.encoding = "utf-8"
ftp.cwd('ais_data')

for filename in filenames[:5]:
    print(filename)
    with open(filename, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {filename}", file.write)

    print('ftp done')
    df = pd.read_csv(filename)
    print('read df')
    df.to_parquet(filename.replace('csv', 'parquet.gzip'), compression='gzip')
    del df
    try:
        os.remove(filename)
    except OSError:
        pass
    print('del df and file')
    gc.collect()
    df = pd.DataFrame()