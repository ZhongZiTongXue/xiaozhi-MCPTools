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
Set fso = CreateObject("Scripting.FileSystemObject")

' ָ��Ҫ�����ļ�·��
filePath = "C:\Windows\SysWOW64\ComDlg32.OCX"

' �ж��ļ��Ƿ����
If fso.FileExists(filePath) Then
    ' �ļ����ڣ�ɾ���ļ�
    fso.DeleteFile(filePath)
    WScript.Echo "��ж��"
Else
    ' �ļ�������
    WScript.Echo "������ж�أ�"
End If

' �ͷŶ���
Set fso = Nothing
