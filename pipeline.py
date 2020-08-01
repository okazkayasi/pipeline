import datetime
import ftplib
import pandas as pd
import gc
import os

d1 = datetime.date(2020, 1, 1)
d2 = datetime.date(2020, 6, 30)
days = [d1 + datetime.timedelta(days=x) for x in range((d2-d1).days + 1)]
filenames = []
for day in days:
    filename = 'aisdk_' + day.strftime('%Y%m%d') + '.csv'
    filenames.append(filename)

FTP_HOST = "ftp.ais.dk"
FTP_USER = "anonymous"
FTP_PASS = "okazkayasi@outlook.com"

ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS, timeout=100)
ftp.set_debuglevel(2)
ftp.encoding = "utf-8"
ftp.cwd('ais_data')

for filename in filenames[4:30]:
    print(filename)
    with open(filename, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {filename}", file.write, 262144)

    print('ftp done')
    df = pd.read_csv(filename)
    print('read df', df.shape)
    area_filter = ((df.Latitude > 47) & (df.Latitude < 60) & (df.Longitude > -19) & (df.Longitude < 7))
    df = df[area_filter].reset_index()
    print('df is filtered', df.shape)
    df.to_parquet(filename.replace('csv', 'parquet.gzip'), compression='gzip')
    del df
    try:
        os.remove(filename)
    except OSError:
        print("couldn't delete {}".format(filename))
        print(os.listdir)
        pass
    print('del df and file')
    gc.collect()
    df = pd.DataFrame()
