'提权
Set WShell = WScript.CreateObject("WScript.Shell")
set fso =CreateObject("Scripting.FileSystemObject")
tFile = "C:\Windows\Logs\用于判断的文件.如报错请删除我"
WShell.run("%comspec% /c echo 123> " & tFile), 0, True
If not fso.FileExists(tFile) then
    CreateObject("Shell.Application").ShellExecute WScript.FullName, Chr(34) & WScript.ScriptFullName & Chr(34), "", "runas", 1
    WScript.Quit
Else
    fso.DeleteFile(tFile)
End if
 
'Msgbox"下面添加你需要执行的代码，此时已有管理员权限了。",0,"提示！"


' 创建FileSystemObject对象
Set fso = CreateObject("Scripting.FileSystemObject")

' 指定要检查的文件路径
filePath = "C:\Windows\SysWOW64\ComDlg32.OCX"

' 判断文件是否存在
If fso.FileExists(filePath) Then
    ' 文件存在，删除文件
    fso.DeleteFile(filePath)
    WScript.Echo "已卸载"
Else
    ' 文件不存在
    WScript.Echo "无需再卸载！"
End If

' 释放对象
Set fso = Nothing
