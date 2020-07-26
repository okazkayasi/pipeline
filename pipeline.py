import datetime
import ftplib
import pyarrow.csv as pv
import pyarrow.parquet as pq

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

for filename in filenames[:2]:
    filename = 'aisdk_20200101.csv'
    with open(filename, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {filename}", file.write)

    table = pv.read_csv(filename)
    pq.write_table(table, filename.replace('csv', 'parquet'))