# sendData
指定された検体について、解析フォルダからiTMSへ送付するデータのシンボリックリンクとチェックサムを作成する。
## 送付データ
### **eWES**
<img src="https://github.com/user-attachments/assets/89825ab3-bb84-4ddb-a4a7-669743ae3881" width="1000">

### **WTS**
<img src="https://github.com/user-attachments/assets/3fdde1cf-4436-4f6e-aca4-f5c8cdf43446" width="1000">

## 実行方法
実行に必要なPythonモジュールがセットされているコンテナ /data1/labTools/labTools.sif を使用する。\
--listfile でリストファイルを指定、または --sample, --batch の両方を指定する。
```
$ singularity exec --bind /data1 /data1/labTools/labTools.sif python sendData.py --help
version: v2.0.0
usage: sendData.py [-h] [--listfile LISTFILE] [--sampleID SAMPLEID] [--batch BATCH] [--directory DIRECTORY] [--forwarding FORWARDING] [--version]

Data Creation Tool for iTMS Sending.

optional arguments:
  -h, --help            show this help message and exit
  --listfile LISTFILE, -f LISTFILE
                        List of samples to be transferred.
  --sampleID SAMPLEID, -s SAMPLEID
                        sample ID
  --batch BATCH, -b BATCH
                        batch folder name
  --directory DIRECTORY, -d DIRECTORY
                        parent analytical directory
  --forwarding FORWARDING, -fw FORWARDING
                        working directory
  --version, -v         show program's version number and exit
```
| option          | 概要                                            |default            |
|:----------------|:------------------------------------------------|:------------------|
|--listfile/-f    |転送する検体のリストファイル。 batchフォルダ名とSample IDをタブ区切りで記載 |None |
|--sampleID/-s    |転送する検体のSample ID（タブ区切りで複数指定可）|None               |
|--batch/-b       |転送する検体のbatchフォルダ名（複数指定不可）    |None               |
|--directory/-d   |解析フォルダの親ディレクトリ                     |/data1/data/result |
|--forwarding/-fw |転送用のデータセット出力先                 |/data1/work/send_to_ITMS |

⇒ \<FORWARDING>/<time‐stamp>/GxD に既定のディレクトリ構造でシンボリックリンクを作成する。\
&ensp;&ensp;&ensp;\<FORWARDING>/<time‐stamp>/checksum.txt に各ファイルのチェックサムを書き出すジョブが投入される。\
⇒ 全てのジョブ完了を確認後、/media/usb に送付用HDDがマウントされていることを確認し、\
&ensp;&ensp;&ensp;rsync -avLzu コマンドで解析データの転送と、\<FORWARDING>/<time‐stamp>/checksum.txt を /media/usb/checksum.txt に追記する。
