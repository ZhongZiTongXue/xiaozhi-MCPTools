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
sourceFilePath = "C:\xiaozhi\MCP\ע��ComDlg32.OCX���\ComDlg32.OCX" ' Դ�ļ�·��
destinationFolderPath = "C:\Windows\SysWOW64" ' Ŀ���ļ���·��
MBWJ = "C:\Windows\SysWOW64\ComDlg32.OCX" ' Դ�ļ�·��

' ���Ŀ���ļ��Ƿ����
If fso.FileExists(MBWJ) Then

'����ע�����
Set sh = CreateObject("Shell.Application")
Sh.ShellExecute "C:\xiaozhi\MCP\ע��ComDlg32.OCX���\ע��ComDlg32.OCX���.bat"

Else
    'WScript.Echo "Ŀ���ļ������ڡ�"
' ���Դ�ļ��Ƿ����
If fso.FileExists(sourceFilePath) Then
    ' ����Ŀ���ļ�������·��
    Dim destinationFilePath
    destinationFilePath = fso.BuildPath(destinationFolderPath, fso.GetFileName(sourceFilePath))
    
    ' �����ļ���Ŀ���ļ���
    fso.CopyFile sourceFilePath, destinationFilePath, True ' True��ʾ���Ŀ���ļ��Ѵ��ڣ��򸲸���
    'WScript.Echo "�ļ��ѳɹ����Ƶ�: " & destinationFilePath

	Wscript.sleep 2000

	'����ע�����
	Set sh = CreateObject("Shell.Application")
	Sh.ShellExecute "C:\xiaozhi\MCP\ע��ComDlg32.OCX���\ע��ComDlg32.OCX���.bat"

Else
    'WScript.Echo "Դ�ļ������ڡ�"
End If

' ����
Set fso = Nothing

End If