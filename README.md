An archive of resources restricted by Russia's Roskomnadzor.


## Summary

This repository stores unredacted data exports that [Roskomnadzor](https://eng.rkn.gov.ru/) provides in XML format. Each XML file is authenticated with Roskomnadzor's detached S/MIME digital signature.

It has two branches:

- `main` serves as the entry point and documentation
- `dump` stores the XML files in a somewhat convoluted format


## Restoring `dump.xml`

```bash
$ git clone -b main https://github.com/fz139/carpaccio.git
$ cd carpaccio
$ git archive dump | tar --extract
$ xargs --arg-file=dump.xml.lst --max-lines=131072 cat >dump.xml
$ git cat-file commit dump | sed --silent '/^SHA1 / { s/// p }' | sha1sum --check
dump.xml: OK
dump.xml.sig: OK
```

This snippet assumes that `dump` is the tree-ish corresponding to the version you want to restore.

## Verifying `dump.xml` signature

You will need the OpenSSL GOST engine and a bundle of Russian CAs.

Debian 13.x (“trixie”) does not include `libengine-gost-openssl`, while both 12.x and 14.x do. Ubuntu 24.04 and 26.04 also package it.

```bash
$ git clone https://github.com/schors/gost-russian-ca.git
$ git clone -b main https://github.com/fz139/carpaccio.git
$ cd carpaccio
$ git archive dump | tar --extract
$ xargs --arg-file=dump.xml.lst --max-lines=131072 cat >dump.xml
$ cd ..
$ docker run --rm -ti -v $PWD:/mnt ubuntu:24.04
# apt-get update && apt-get install -y openssl libengine-gost-openssl
# c_rehash /mnt/gost-russian-ca/certs

# : git-archive(1) sets mtime to author date; the field is set to signingTime
# iat=$(stat --format %Y /mnt/carpaccio/dump.xml.sig)

# : some signing keys have non-S/MIME purpose
# pur=
# openssl cms -inform DER -in dump.xml.sig -cmsout -print |
>   grep -F 0x63002A0E7BFC2B588B0959E779BAE786CF9DA227 && pur="-purpose sslserver"

# openssl smime -verify -engine gost -CApath /mnt/gost-russian-ca/certs -out /dev/null \
>   -in dump.xml.sig -inform DER -content dump.xml -attime "$iat" $pur
Engine "gost" set.
Verification successful
```


## Why?!

TL;DR: to save storage and CPU.

`dump.xml` is split into content-defined chunks, and the chunks are renamed using content-derived names to help Git store the dump efficiently.

Using fixed-size chunks causes the repository to grow beyond 100 GiB and takes over five hours to `clone` on an Intel Core i7-10750H machine connected via Gigabit Ethernet.

Content-defined chunks without content-derived names still result in the repository growing beyond 18 GiB.

The current format is the fifth iteration of lossless compression for this cursed dataset.


## Конвертер XML в CSV в формат https://github.com/zapret-info/z-i

Запускается так:

```python
python parse_dump_xml.py dump.xml -o dump.csv
```

Перед этим можно объединить файлы в 1 xml файл так:

```powershell
powershell -Command "Get-Content carpaccio/dump.xml.lst | ForEach-Object { Get-Content carpaccio/$_ -Raw } | Set-Content dump.xml"
```

## analyze.py

Анализатор дампа на наличие ключевых слов с выводом анализа в txt-файлы.
Список групп и слов задается внутри файла `config.yaml`.

## Полный скрипт для анализа дампа в Windows

```
if not exist "results" mkdir results

REM Один раз нужно в начале выполнить `git clone -b main https://github.com/fz139/carpaccio.git`.
cd carpaccio
git pull
cd ..

powershell -Command "Get-Content carpaccio/dump.xml.lst | ForEach-Object { Get-Content carpaccio/$_ -Raw } | Set-Content results/dump.xml"

python parse_dump_xml.py "results\dump.xml" -o "results\dump.csv"
copy /Y "results\dump.csv" csv_delta

python analyze.py > results/result.txt
```

