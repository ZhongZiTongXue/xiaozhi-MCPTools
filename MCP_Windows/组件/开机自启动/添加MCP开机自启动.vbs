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
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

' 指定源文件路径和目标文件夹路径
Dim sourceFilePath, destinationFolderPath
sourceFilePath = "C:\xiaozhi\MCP\MCP_Windows\组件\开机自启动\小智Ai_MCP_自启动服务.lnk" ' 源文件路径
destinationFolderPath = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" ' 目标文件夹路径


If fso.FileExists(sourceFilePath) Then
    ' 构建目标文件的完整路径
    Dim destinationFilePath
    destinationFilePath = fso.BuildPath(destinationFolderPath, fso.GetFileName(sourceFilePath))
    
    ' 复制文件到目标文件夹
    fso.CopyFile sourceFilePath, destinationFilePath, True ' True表示如果目标文件已存在，则覆盖它
    'WScript.Echo "文件已成功复制到: " & destinationFilePath

Else
    WScript.Echo "源文件不存在。"
End If

' 清理
Set fso = Nothing