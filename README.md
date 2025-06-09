# sendData
指定された検体について、解析フォルダからiTMSへ送付するデータのシンボリックリンクとチェックサムを作成する。
## 送付データ
### **eWES**
<img src="https://github.com/user-attachments/assets/cd1eb924-470a-4087-b647-d831edc29c51" width="1000">

### **WTS**
<img src="https://github.com/user-attachments/assets/67533440-aa2c-4a35-8c6f-3020910bd0f6" width="1000">

## 実行方法
実行に必要なPythonモジュールがセットされているコンテナ /data1/labTools/labTools.sif を使用する。\
--listfile でリストファイルを指定、または --sample, --batch の両方を指定する。
```
$ singularity exec --bind /data1 /data1/labTools/labTools.sif python /data1/labTools/sendData/latest/sendData.py --help
version: v2.0.0
usage: sendData.py [-h] [--listfile LISTFILE] [--sampleID SAMPLEID] [--batch BATCH]
                   [--directory DIRECTORY] [--transfer TRANSFER] [--version]

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
  --transfer TRANSFER, -t TRANSFER
                        working directory
  --version, -v         show program's version number and exit
```
| option        |required | 概要                                            |default            |
|:--------------|:-------:|:------------------------------------------------|:------------------|
|--listfile/-f  |False*   |転送する検体のリストファイル。 batchフォルダ名とSample IDをタブ区切りで記載 |None |
|--sampleID/-s  |False*   |転送する検体のSample ID（タブ区切りで複数指定可）|None               |
|--batch/-b     |False*   |転送する検体のbatchフォルダ名（複数指定不可）    |None               |
|--directory/-d |False    |解析フォルダの親ディレクトリ                     |/data1/data/result |
|--transfer/-t  |False    |転送用のデータセット出力先                 |/data1/work/send_to_ITMS |

**\*--listfile または --sampleID と--batch を指定する** \
⇒ \<TRANSFER\>/\<timestamp\>/GxD に既定のディレクトリ構造でシンボリックリンクが作成される。\
&ensp;&ensp;&ensp;\<TRANSFER\>/\<timestamp\>/checksum.txt に各ファイルのチェックサムを書き出すジョブが投入される。\
⇒ 投入された全てのジョブ完了を確認後、/media/usb/cap に送付用HDDがマウントされていることを確認し、\
&ensp;&ensp;&ensp;rsync -avLzu コマンドで解析データの転送と、\<TRANSFER\>/\<timestamp\>/checksum.txt の /media/usb/cap/checksum.txt への追記を実施する。
