import datetime
import subprocess

date = datetime.datetime.now().strftime('%d-%m-%y -> %H:%M')

print('Processo iniciado...')
subprocess.run(['clear'])
print('Realizando checagem de erros...')
subprocess.run(['ruff', 'check', '.'])
subprocess.run(['clear'])
print('Realizando commit...')
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', date])
subprocess.run(['git', 'push', 'origin', 'main'])
subprocess.run(['clear'])
print('Processo finalizado com sucesso!')