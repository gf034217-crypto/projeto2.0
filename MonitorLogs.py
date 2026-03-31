import random
import datetime

def menu():
    nome_arq = "log.txt"
    while True:
        print('monitor LogPy')
        print('1 - gerar logs')
        print('2 - Analisar logs')
        print('3 - gerar e analisar logs')
        print('4 - sair')
        opcao = input('escolha uma opção:')
        if opcao == '1':
            try:
                qtd = int(input('quantidade de logs'))
                gerarArquivo(nome_arq, qtd)
            except:
                print("qtd incorreta")
        elif opcao == '2':
            analisarLog(nome_arq)
        elif opcao == '3':
            try:
                qtd = int(input('qtd de logs'))
                gerarArquivo(nome_arq, qtd)
                analisarLog(nome_arq)
            except:
                print('qtd incorreta')
        elif opcao == '4':
            print('até mais')
            break
        else:
            print('opção errada')

def gerarArquivo(nome_arq, qtd):
    with open(nome_arq, 'w', encoding='UTF -8') as nome_arq:
        for i in range(qtd):
            arq.write(montarLog(i) + '\n')
            print('Logs gerados')
def montarLog(i):
    data = gerarDataHora(i)
    ip = gerarIp(i)
    recurso = gerarRecurso(i)
    metodo = gerarMetodo(i)
    status = gerarStatus(i)
    tempo = gerarTempo(i)
    agent = gerarAgent(i)
    return f'[{data}] - {ip} - {metodo} - {status} - {recurso} - {tempo}ms - 500mb - HTTP/1.1 {agent} - /home'

def gerarDataHora(i):
    base = datetime.datetime(2026, 3, 30,22,8,0)
    data = datetime.timedelta(seconds=i * random.randint(5,20))
    return (base + data).strftime('%d/%m/%Y %H:%M:%S')
def gerarIp(i):
    r = random.randint(1,6)

    if i >= 20 and i <=30:
        return "200.0.111.345"
    if r == 1:
        return '192.168.5.6'
    elif r == 2:
        return "192.168.5.8"
    elif r == 3:
        return "192.168.5.9"
    elif r == 4:
        return "192.168.25.8"
    elif r == 5:
        return "192.168.45.8"
    else:
        return "192.168.65.68"

