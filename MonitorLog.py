import random
import datetime

#Gabriel dos Santos Ferreira RGM: 47086921
#Matheus Freitas Hilario de Moraes RGM:047403012

# GERAÇÃO


def gerar_data_hora(i):
    base = datetime.datetime(2026, 3, 30, 22, 0, 0)
    delta = datetime.timedelta(seconds=i * random.randint(5, 20))
    return (base + delta).strftime("%d/%m/%Y %H:%M:%S")

def gerar_ip(i):
    if 20 <= i <= 30:
        return "200.0.111.345"
    return f"192.168.0.{random.randint(1,10)}"

def gerar_recurso():
    r = random.randint(1, 8)
    if r == 1: return "/admin"
    if r == 2: return "/login"
    if r == 3: return "/backup"
    if r == 4: return "/config"
    if r == 5: return "/private"
    if r == 6: return "/produtos"
    if r == 7: return "/home"
    return "/contato"

def gerar_metodo(r):
    if r == "/login":
        return "POST"
    return "GET"

def gerar_status(i, r):
    if 20 <= i <= 25:
        return 500
    if r == "/login" and i % 3 == 0:
        return 403
    if r == "/admin" and random.randint(1,2) == 1:
        return 403
    if random.randint(1,15) == 1:
        return 500
    if random.randint(1,10) == 1:
        return 404
    return 200

def gerar_tempo(i, s):
    base = random.randint(50, 900)
    if s == 500:
        return base + random.randint(500,1000)
    if s == 403:
        return base + random.randint(200,400)
    if 40 <= i <= 45:
        return i * 150
    return base

def gerar_user_agent():
    r = random.randint(1,10)
    if r == 1: return "GoogleBot"
    if r == 2: return "CrawlerX"
    if r == 3: return "SpiderNet"
    return "Chrome"

def gerar_arquivo_logs(nome, qtd):
    with open(nome, "w") as arq:
        for i in range(qtd):
            data = gerar_data_hora(i)
            ip = gerar_ip(i)
            r = gerar_recurso()
            m = gerar_metodo(r)
            s = gerar_status(i, r)
            t = gerar_tempo(i, s)
            a = gerar_user_agent()

            linha = f"[{data}] {ip} - {m} - {s} - {r} - {t}ms - 500B - HTTP/1.1 - {a} - /home\n"
            arq.write(linha)


# PARSING MANUAL


def extrair_campo(linha, inicio):
    campo = ""
    i = inicio

    while i < len(linha) and linha[i] != "-":
        campo += linha[i]
        i += 1

    return campo.strip(), i + 1

def extrair_tempo(linha):
    i = 0
    while i < len(linha):
        if linha[i] == "m" and linha[i+1] == "s":
            j = i - 1
            num = ""
            while j >= 0 and linha[j].isdigit():
                num = linha[j] + num
                j -= 1
            return int(num)
        i += 1
    return 0


# ANÁLISE


def analisar_arquivo_logs(nome):
    with open(nome, "r") as arq:

        total = sucesso = erro = erro_critico = 0
        soma = maior = 0
        menor = 999999

        rapido = normal = lento = 0
        s200 = s403 = s404 = s500 = 0

        recurso_contagem = {}
        ip_contagem = {}
        ip_erros = {}

        brute = 0
        ultimo_brute = ""
        seq_403 = 0
        ultimo_ip_403 = ""

        falha_critica = 0
        seq_500 = 0

        degradacao = 0
        crescente = 0
        ultimo_tempo = -1

        bot = 0
        ultimo_bot = ""
        seq_ip = 0
        ultimo_ip = ""

        sensiveis = 0
        sensiveis_erro = 0

        for linha in arq:
            total += 1

            # IP
            i = linha.find("]") + 2
            ip, i = extrair_campo(linha, i)

            # método
            metodo, i = extrair_campo(linha, i)

            # status
            status_str, i = extrair_campo(linha, i)
            status = int(status_str)

            # recurso
            recurso, i = extrair_campo(linha, i)

            # tempo
            tempo = extrair_tempo(linha)

            # contagem recurso
            if recurso not in recurso_contagem:
                recurso_contagem[recurso] = 0
            recurso_contagem[recurso] += 1

            # contagem ip
            if ip not in ip_contagem:
                ip_contagem[ip] = 0
            ip_contagem[ip] += 1

            if status != 200:
                if ip not in ip_erros:
                    ip_erros[ip] = 0
                ip_erros[ip] += 1

            # status
            if status == 200:
                sucesso += 1
                s200 += 1
                seq_403 = 0
                seq_500 = 0
            elif status == 403:
                erro += 1
                s403 += 1
                if ip == ultimo_ip_403:
                    seq_403 += 1
                else:
                    seq_403 = 1
                ultimo_ip_403 = ip
            elif status == 404:
                erro += 1
                s404 += 1
                seq_403 = 0
            elif status == 500:
                erro += 1
                erro_critico += 1
                s500 += 1
                seq_500 += 1

            # brute force
            if seq_403 >= 3 and recurso == "/login":
                brute += 1
                ultimo_brute = ip

            # falha crítica
            if seq_500 >= 3:
                falha_critica += 1

            # tempo
            soma += tempo
            if tempo > maior: maior = tempo
            if tempo < menor: menor = tempo

            if tempo < 200: rapido += 1
            elif tempo < 800: normal += 1
            else: lento += 1

            # degradação
            if tempo > ultimo_tempo:
                crescente += 1
                if crescente >= 3:
                    degradacao += 1
            else:
                crescente = 0
            ultimo_tempo = tempo

            # bot por user agent
            if "Bot" in linha or "Crawler" in linha or "Spider" in linha:
                bot += 1
                ultimo_bot = ip

            # bot por repetição
            if ip == ultimo_ip:
                seq_ip += 1
                if seq_ip >= 5:
                    bot += 1
                    ultimo_bot = ip
            else:
                seq_ip = 0
            ultimo_ip = ip

            # rotas sensíveis
            if recurso in ["/admin","/backup","/config","/private"]:
                sensiveis += 1
                if status != 200:
                    sensiveis_erro += 1

        # pós processamento
        disponibilidade = (sucesso/total)*100
        taxa_erro = (erro/total)*100
        media = soma/total

        # recurso mais acessado
        recurso_top = max(recurso_contagem, key=recurso_contagem.get)

        # ip mais ativo
        ip_top = max(ip_contagem, key=ip_contagem.get)

        # ip com mais erros
        ip_erro_top = max(ip_erros, key=ip_erros.get) if ip_erros else "nenhum"

        # estado
        if falha_critica > 0 or disponibilidade < 70:
            estado = "CRÍTICO"
        elif disponibilidade < 85 or lento > normal:
            estado = "INSTÁVEL"
        elif disponibilidade < 95 or bot > 0:
            estado = "ATENÇÃO"
        else:
            estado = "SAUDÁVEL"

        print("\n===== MONITOR LOGPY =====")
        print('VISÃO GERAL')
        print("Total de acessos:", total)
        print("Total de sucessos:", sucesso)
        print("Total de erros:", erro)
        print("Total de erros críticos:", erro_critico)
        print("Disponibilidade:", disponibilidade,'%')
        print("Taxa erro:", taxa_erro,'%')
        print('     ')
        print('DESEMPENHO')
        print("Tempo médio:", media, 'ms')
        print("Maior tempo:", maior, 'ms')
        print("Menor tempo:", menor, 'ms')
        print("Rápidos:", rapido)
        print("Normais:", normal)
        print("Lentos:", lento)
        print('     ')
        print('STATUS HTTP')
        print("200:", s200)
        print("403:", s403)
        print("404:", s404)
        print("500:", s500)
        print('     ')
        print('ACESSO')
        print("Recurso mais acessado(aprox):", recurso_top)
        print("IP mais ativo(aprox):", ip_top)
        print("IP com mais erros(aprox):", ip_erro_top)
        print('     ')
        print('SEGURANÇA')
        print("Força bruta:", brute)
        print("Último brute:", ultimo_brute)
        print("Admin erros:", sensiveis_erro)
        print("Bots:", bot)
        print("Último bot:", ultimo_bot)
        print('     ')
        print('RISCOS')
        print("Acessos rotas sensíveis:", sensiveis)
        print("Falhas rotas sensíveis:", sensiveis_erro)
        print("Degradação:", degradacao)
        print("Falha críticas:", falha_critica)
        print('     ')
        print('ESTADO FINAL')
        print("Situação do Sistema:", estado)
        print('=========================')


# MENU


def menu():
    nome = "log.txt"

    while True:
        print("\n1 - Gerar logs")
        print("2 - Analisar logs")
        print("3 - Gerar e analisar")
        print("4 - Sair")

        op = input("Escolha: ")

        if op == "1":
            try:
                qtd = int(input(f'Quantidade de logs:'))
                gerar_arquivo_logs(nome, qtd)
            except:
                print('Quantidade invalida!')
        elif op == "2":
            analisar_arquivo_logs(nome)
        elif op == "3":
            try:
                qtd = int(input(f'Quantidade de logs:'))
                gerar_arquivo_logs(nome, qtd)
                analisar_arquivo_logs(nome)
            except:
                print('Quantidade invalida!')
            
            
        elif op == "4":
            print('Seção encerrada')
            break
        else:
            print("Opção inválida")

menu()