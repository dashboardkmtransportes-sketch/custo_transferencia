Set WshShell = CreateObject("WScript.Shell")

' Define o comando para executar o Streamlit
' O caminho para o arquivo .py é relativo à localização do script VBS
comando = "streamlit run dashboard_transferencia.py"

' Executa o comando de forma invisível (o "0")
WshShell.Run comando, 0

Set WshShell = Nothing
