'��Ȩ
Set WShell = WScript.CreateObject("WScript.Shell")
set fso =CreateObject("Scripting.FileSystemObject")
tFile = "C:\Windows\Logs\�����жϵ��ļ�.�籨����ɾ����"
WShell.run("%comspec% /c echo 123> " & tFile), 0, True
If not fso.FileExists(tFile) then
    CreateObject("Shell.Application").ShellExecute WScript.FullName, Chr(34) & WScript.ScriptFullName & Chr(34), "", "runas", 1
    WScript.Quit
Else
    fso.DeleteFile(tFile)
End if
 
'Msgbox"�����������Ҫִ�еĴ��룬��ʱ���й���ԱȨ���ˡ�",0,"��ʾ��"

' ����FileSystemObject����
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

' ָ��Դ�ļ�·����Ŀ���ļ���·��
Dim sourceFilePath, destinationFolderPath
sourceFilePath = "C:\xiaozhi\MCP\MCP_Windows\���\����������\С��Ai_MCP_����������.lnk" ' Դ�ļ�·��
destinationFolderPath = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" ' Ŀ���ļ���·��


If fso.FileExists(sourceFilePath) Then
    ' ����Ŀ���ļ�������·��
    Dim destinationFilePath
    destinationFilePath = fso.BuildPath(destinationFolderPath, fso.GetFileName(sourceFilePath))
    
    ' �����ļ���Ŀ���ļ���
    fso.CopyFile sourceFilePath, destinationFilePath, True ' True��ʾ���Ŀ���ļ��Ѵ��ڣ��򸲸���
    'WScript.Echo "�ļ��ѳɹ����Ƶ�: " & destinationFilePath

Else
    WScript.Echo "Դ�ļ������ڡ�"
End If

' ����
Set fso = Nothing