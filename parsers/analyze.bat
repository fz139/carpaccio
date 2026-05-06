if not exist "results" mkdir results

REM Один раз перед первым запуском нужно выполнить:
REM pip install -r requirements.txt
REM git clone -b main https://github.com/fz139/carpaccio.git

cd carpaccio
git pull
git checkout dump
cd ..

powershell -Command "Get-Content carpaccio/dump.xml.lst | ForEach-Object { Get-Content carpaccio/$_ -Raw } | Set-Content results/dump.xml"

python parse_dump_xml.py "results\dump.xml" -o "results\dump.csv"
copy /Y "results\dump.csv" csv_delta

python analyze.py > results/result.txt
