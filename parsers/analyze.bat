if not exist "results" mkdir results

REM Один раз нужно в начале выполнить `git clone -b main https://github.com/fz139/carpaccio.git`.
cd carpaccio
git pull
cd ..

powershell -Command "Get-Content carpaccio/dump.xml.lst | ForEach-Object { Get-Content carpaccio/$_ -Raw } | Set-Content results/dump.xml"

python parse_dump_xml.py "results\dump.xml" -o "results\dump.csv"
copy /Y "results\dump.csv" csv_delta

python analyze.py > results/result.txt
