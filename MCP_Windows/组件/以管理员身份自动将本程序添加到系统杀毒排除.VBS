'提权
Set WShell = WScript.CreateObject("WScript.Shell")
set fso =CreateObject("Scripting.FileSystemObject")
tFile = "C:\Windows\System32\drivers\etc\test.txt"
WShell.run("%comspec% /c echo 123> " & tFile), 0, True
if not fso.FileExists(tFile) then
    CreateObject("Shell.Application").ShellExecute WScript.FullName, Chr(34) & WScript.ScriptFullName & Chr(34), "", "runas", 1
    WScript.Quit
else
    fso.DeleteFile(tFile)
End if
 
'Wscript.echo "下面添加你需要执行的代码，此时已有管理员权限了。"


Set objShell = CreateObject("WScript.Shell")

strFolderPath = "C:\xiaozhi" ' 修改为你想要排除的文件夹路径

' 用 PowerShell 命令添加排除项
strCommand = "powershell -Command ""Add-MpPreference -ExclusionPath '" & strFolderPath & "'"""

objShell.Run strCommand, 0, True

WScript.Echo "已自动将小智MCP程序文件夹！" & vbCrLf & "添加到 Windows Defender 杀毒排除项！" & vbCrLf & "尽可能的保证程程序在运行时不受误报毒干扰！"