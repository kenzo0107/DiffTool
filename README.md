# リモート & ローカル バックアップツール

- リモートサーバとローカルサーバの対象ファイルの比較差分をする目的で作成しました。

## 使い方

#### 1. file.list に差分比較対象ファイル記載

```
components/utility.go
models/person.go
```

#### 2. コマンド実行

```
$ python diffrelo.py -t <hostname> -re <Remote workspace> -lo <Local workspace> -f <diff files list>
```

例) 
```
$ python diffrelo.py -t hoge -re /var/www/html/hoge-project -lo ~/go/src/github.com/hoge -f file.list

---------------------------------------
Remote Server (Alias): hoge
remote : /var/www/html/hoge-project
local  : ~/go/src/github.com/hoge
list   : file.list
---------------------------------------

Delete tmp remote directory [./tmp/Remote/]
Delete tmp local directory [./tmp/Local/]

components/utility.go
[Remote Server] ---> [Local:./tmp/Remote/]
[Local workspace] ---> [Local:./tmp/Local/]

models/person.go
[Remote Server] ---> [Local:./tmp/Remote/]
[Local workspace] ---> [Local:./tmp/Local/]

--------------------------------------
Difference between LOCAL & REMOTE
--------------------------------------
components/utility.go

--------------------------------------
New Files
--------------------------------------
models/person.go

Finish ! (^-^)/Bye!
```

- Difference between LOCAL & REMOTE ... ローカルとリモートサーバで差分があったファイル一覧
- New Files ... 新規ファイル (リモートファイルには存在しないファイル)

