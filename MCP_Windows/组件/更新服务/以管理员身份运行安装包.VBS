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

Set sh = CreateObject("Shell.Application")
Sh.ShellExecute "C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\小智Ai-MCP链接工具_新版本安装包.exe"
