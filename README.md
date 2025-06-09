# sendData
指定された検体について、iTMSへ送付するデータのシンボリックリンクとチェックサムを作成する。
## 送付データ
### **eWES**
<img src="https://github.com/user-attachments/assets/cd1eb924-470a-4087-b647-d831edc29c51" width="1000">

### **WTS**
<img src="https://github.com/user-attachments/assets/67533440-aa2c-4a35-8c6f-3020910bd0f6" width="1000">

## エイリアスの作成（初回のみ）
~/bin フォルダを作成し、以下のコマンドを記載したテキストファイル send_to_itms を作成し、実行権限を付与する。
エイリアスを作成しない場合は、singularity でコンテナを指定して実行する。
```
singularity exec --disable-cache --bind /data1 /data1/labTools/labTools.sif python /data1/labTools/sendData/latest/sendData.py $@
```
usage を表示してエイリアスの設定を確認する。以下が表示されればOK。
```
$ send_to_itms -h
version: v2.0.0
usage: sendData.py [-h] [--listfile LISTFILE] [--sample SAMPLE] [--batch BATCH]
                   [--directory DIRECTORY] [--transfer TRANSFER] [--version]

Data Creation Tool for iTMS Sending.

optional arguments:
  -h, --help            show this help message and exit
  --listfile LISTFILE, -f LISTFILE
                        List of samples to be transferred.
  --sample SAMPLE, -s SAMPLE
                        sample ID
  --batch BATCH, -b BATCH
                        batch folder name
  --directory DIRECTORY, -d DIRECTORY
                        parent analytical directory
  --transfer TRANSFER, -t TRANSFER
                        working directory
  --version, -v         show program's version number and exit
```
## 実行方法
--listfile でリストファイルを指定、または --sample, --batch の両方を指定する。
```
$ send_to_itms --listfile <送付するサンプルリストファイルパス>
$ send_to_itms --batch <送付するサンプルのバッチフォルダ名> --sample <送付するサンプルID>
```
| option        |required | 概要                                            |default            |
|:--------------|:-------:|:------------------------------------------------|:------------------|
|--listfile/-f  |False*   |転送する検体のリストのファイルパス。<br> batchフォルダ名とSample IDをタブ区切りで記載 |None |
|--sample/-s    |False*   |転送する検体のSample ID（タブ区切りで複数指定可）|None               |
|--batch/-b     |False*   |転送する検体のbatchフォルダ名（複数指定不可）    |None               |
|--directory/-d |False    |解析フォルダの親ディレクトリ                     |/data1/data/result |
|--transfer/-t  |False    |転送用のデータセット出力先                 |/data1/work/send_to_ITMS |

**\*--listfile または --sample と--batch を指定する** \
⇒ \<TRANSFER\>/\<timestamp\>/GxD に既定のディレクトリ構造でシンボリックリンクが作成される。\
&ensp;&ensp;&ensp;\<TRANSFER\>/\<timestamp\>/checksum.txt に各ファイルのチェックサムを書き出すジョブが投入される。\
⇒ 投入された全てのジョブ完了を確認後、/media/usb/cap に送付用HDDがマウントされていることを確認し、\
&ensp;&ensp;&ensp;rsync -avLzu コマンドで解析データの転送と、\<TRANSFER\>/\<timestamp\>/checksum.txt の /media/usb/cap/checksum.txt への追記を実施する。
