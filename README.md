# sendData
指定された検体について、解析フォルダからiTMSへ送付するデータのシンボリックリンクとチェックサムを作成する。

## 実行方法
実行に必要なPythonモジュールがセットされているコンテナ /data1/labTools/labTools.sif を使用する。\
--listfile でリストファイルを指定、または --sample, --batch の両方を指定する。
```
singularity exec --bind /data1 /data1/labTools/labTools.sif python sendData.py --help
version: v2.0.0
usage: sendData.py [-h] [--listfile LISTFILE] [--sampleID SAMPLEID] [--batch BATCH] [--workdir WORKDIR] [--version]

Data Creation Tool for iTMS Sending.

optional arguments:
  -h, --help            show this help message and exit
  --listfile LISTFILE, -f LISTFILE
                        List of samples to be transferred.
  --sampleID SAMPLEID, -s SAMPLEID
                        sample ID
  --batch BATCH, -b BATCH
                        batch folder name
  --workdir WORKDIR, -wd WORKDIR
                        working directory
  --version, -v         show program's version number and exit
```
| option       | 概要                                     |default         |
|:-------------|:-----------------------------------------|:---------------|
|--listfile/-f |転送する検体のリストファイル。 batchフォルダ名とSample IDをタブ区切りで記載 |None |
|--sampleID/-s |転送する検体のSample ID（タブ区切りで複数指定可）|None |
|--batch/-b    |転送する検体のbatchフォルダ名（複数指定不可）|None |
|--workdir/-wd |転送用のデータセット出力先 |/data1/work/send_to_ITMS |

⇒ \<workdir>/<time‐stamp>/GxD に既定のディレクトリ構造でシンボリックリンクを作成する。\
&ensp;&ensp;&ensp;\<workdir>/<time‐stamp>/checksum.txt に各ファイルのチェックサムを書き出すジョブが投入される。\
⇒ 全てのジョブ完了を確認後、/media/usb に送付用HDDがマウントされていることを確認し、\
&ensp;&ensp;&ensp;rsync -avLzu コマンドで解析データの転送と、\<workdir>/<time‐stamp>/checksum.txt を /media/usb/checksum.txt に追記する。
<p align="center">
    <img src="https://github.com/user-attachments/assets/c9ea0932-06ca-4dec-9d63-ff7066f49744" width="600">
</p>
