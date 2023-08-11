menu = '''

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=>'''

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

def verificar_decimal(numero):
    decimal = numero.split('.')[1]
    if len(decimal) > 2:
        print('Valor inválido, por favor insira um valor com até duas casas decimais.')
        return False
    
    else:
        return True
    
def deposito(saldo, extrato):

    str_valor_deposito = input('Informe o valor do depósito ou digite "c" para cancelar: ')
    if str_valor_deposito == "c":
        return False, saldo, extrato
    
    valor_deposito = float(str_valor_deposito)
    if valor_deposito <= 0:
        print('Valor inválido, por favor informe um valor acima de zero.')
        return True, saldo, extrato
    else:
        if '.' in str_valor_deposito:
            if verificar_decimal(str_valor_deposito) == False:
                return True, saldo, extrato
        
        saldo += valor_deposito
        extrato = extrato + f"\nDepósito: + R$ {valor_deposito:.2f}"
        print('Depósito realizado com sucesso!')
        return False, saldo, extrato
    
def saque(saldo, limite, extrato, numero_saques, LIMITE_SAQUES):
    if saldo <= 0:
        print("Você não possui saldo em conta.")
        return False, saldo, extrato, numero_saques
    elif numero_saques == LIMITE_SAQUES:
        print("Você já atingiu o limite diário de saques")
        return False, saldo, extrato, numero_saques
    
    else:
        str_valor_saque = input('Informe o valor do saque ou digite "c" para cancelar: ')
        if str_valor_saque == "c":
            return False, saldo, extrato, numero_saques
        
        valor_saque = float(str_valor_saque)


        if '.' in str_valor_saque:
            if verificar_decimal(str_valor_saque) == False:
                return True, saldo, extrato, numero_saques
            
        if valor_saque > limite:
            print(f'O valor informado de R$ {valor_saque:.2f} está acima do seu limite de R$ {limite:.2f} por saque. Por favor, informe um valor correto.')
            return True, saldo, extrato, numero_saques
        
        if valor_saque > saldo:
            print(f'Saldo insuficiente.')
            return True, saldo, extrato, numero_saques
        
        else:
            numero_saques += 1
            saldo -= valor_saque
            extrato = extrato + f"\nSaque: - R$ {valor_saque:.2f}"    
            print("Saque realizado com sucesso!")
            return False, saldo, extrato, numero_saques

while True:

    opcao = input(menu)

    if opcao == "d":
        depositar = True
        while depositar == True:
            depositar, saldo, extrato = deposito(saldo, extrato)

    elif opcao == "s":
        sacar = True
        while sacar == True:
            sacar, saldo, extrato, numero_saques = saque(saldo, limite, extrato, numero_saques, LIMITE_SAQUES)
    
    elif opcao == "e":
        print("\n==========Extrato==========")
        print("Não foram realizadas movimentações" if not extrato else extrato)
        print(f"\nSaldo: R$ {saldo:.2f}")
        print("============================")

    elif opcao == "q":
        break

    else:
        print("Operação inválida, por favor selecione novamente a opção desejada.")