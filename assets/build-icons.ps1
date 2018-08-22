Remove-Item dicognito*.png
python build_icons.py
Get-ChildItem dicognito*.png | ForEach-Object { pngout /c0  $_ }