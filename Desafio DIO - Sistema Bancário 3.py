# Sistema bancário seguindo o paradigma de classes.
# * - todos os argumentos após a * são nomeados
# / - todos os argumentos antes do / são posicionais
import textwrap
from abc import ABC, abstractclassmethod

class Cliente:
    def __init__(self, endereco:str):
        self.endereco = endereco
        self.contas=[]
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_de_nascimento, endereco):
        self.cpf = cpf
        self.nome = nome
        self.data_de_nascimento = data_de_nascimento
        super().__init__(endereco)

class Conta:
    def __init__(self, numero, cliente):
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._saldo = 0
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)    

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        pass

    def depositar(self, valor):
        pass

class ContaCorrente(Conta):
    def __init__(self, limite, limite_de_saques, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limite = limite
        self.limite_de_saques = limite_de_saques

class Historico:
    pass

class Transacao(ABC):
    def regitrar(self, conta):
        pass

class Saque(Transacao):
    pass

class Deposito(Transacao):
    pass
    
def menu():

    menu = '''
    ══════════════ MENU ══════════════
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tListar Contas
    [nu]\tNovo Usuário
    [q]\tSair
    ► '''
    return input(textwrap.dedent(menu))

def verificar_decimal(numero):
    decimal = numero.split('.')[1]
    if len(decimal) > 2:
        print('ERRO: Valor inválido, por favor insira um valor com até duas casas decimais.')
        return False
    
    else:
        return True

def deposito(saldo, extrato, /):

    str_valor_deposito = input('Informe o valor do depósito ou digite "c" para cancelar: ')
    if str_valor_deposito == "c":
        return False, saldo, extrato
    
    valor_deposito = float(str_valor_deposito)
    if valor_deposito <= 0:
        print('ERRO: Valor inválido, por favor informe um valor acima de zero.')
        return True, saldo, extrato
    else:
        if '.' in str_valor_deposito:
            if verificar_decimal(str_valor_deposito) == False:
                return True, saldo, extrato
        
        saldo += valor_deposito
        extrato = extrato + f"\nDepósito:\t+ R$ {valor_deposito:.2f}"
        print('Depósito realizado com sucesso!')
        return False, saldo, extrato

def saque(*, saldo, limite, extrato, numero_saques, LIMITE_SAQUES):
    if saldo <= 0:
        print("ERRO: Você não possui saldo em conta.")
        return False, saldo, extrato, numero_saques
    elif numero_saques == LIMITE_SAQUES:
        print("ERRO: Você já atingiu o limite diário de saques")
        return False, saldo, extrato, numero_saques
    
    else:
        str_valor_saque = input('Informe o valor do saque ou digite "c" para cancelar: ')
        if str_valor_saque == "c":
            return False, saldo, extrato, numero_saques
        
        valor_saque = float(str_valor_saque)

        if valor_saque <= 0:
            print('ERRO: Valor inválido, por favor informe um valor acima de zero.')
            return True, saldo, extrato, numero_saques
        
        if '.' in str_valor_saque:
            if verificar_decimal(str_valor_saque) == False:
                return True, saldo, extrato, numero_saques
            
        if valor_saque > limite:
            print(f'ERRO: O valor informado de R$ {valor_saque:.2f} está acima do seu limite de R$ {limite:.2f} por saque. Por favor, informe um valor correto.')
            return True, saldo, extrato, numero_saques
        
        if valor_saque > saldo:
            print(f'ERRO: Saldo insuficiente.')
            return True, saldo, extrato, numero_saques
        
        else:
            numero_saques += 1
            saldo -= valor_saque
            extrato = extrato + f"\nSaque:\t\t- R$ {valor_saque:.2f}"    
            print("Saque realizado com sucesso!")
            return False, saldo, extrato, numero_saques

def exibir_extrato(saldo,/ ,* , extrato):
    print("\n══════════════ Extrato ══════════════")
    print(f"\nSaldo:\t\tR$ {saldo:.2f}")
    print("Não foram realizadas movimentações" if not extrato else extrato)
    print("═════════════════════════════════════")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario['CPF'] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def novo_usuario(usuarios):
    cpf = input('Insira seu CPF (apenas números): ')
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("\n ERRO: Este CPF já está vinculado a um usuário.")
        return
    
    nome = input("Nome completo: ")
    data_de_nascimento = input("Data de Nascimento (DD-MM-AAAA): ")
    endereco = input("Endereço (Logradouro, Número - Bairro - Cidade/UF): ")

    usuarios.append({'Nome': nome, 'Data de Nascimento': data_de_nascimento, 'CPF': cpf, 'Endereço': endereco})
    print('Usuário criado com sucesso!')

def nova_conta(AGENCIA, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)
    numero_da_conta = len(contas) + 1
    
    if usuario:
        print('Conta criada com sucesso!')
        contas.append({'Agência':AGENCIA, 'Número da Conta': numero_da_conta, 'Usuário':usuario})
        return
    
    print('ERRO: Usuário não encontrado. Por favor, cadastre novo usuário antes de abrir uma nova conta.')

def listar_contas(contas):
    for conta in contas:
        linha = f"""\
            Agência:\t{conta['Agência']}
            C/C:\t\t{conta['Número da Conta']}
            Titular:\t{conta['Usuário']['Nome']}
        """
        print('═' * 100)
        texto = textwrap.dedent(linha)
        print(texto)

def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0

    usuarios = []
    contas = []
    
    while True:

        opcao = menu()

        if opcao == "d":
            depositar = True
            while depositar == True:
                depositar, saldo, extrato = deposito(saldo, extrato)

        elif opcao == "s":
            sacar = True
            while sacar == True:
                sacar, saldo, extrato, numero_saques = saque(
                    saldo=saldo, 
                    limite=limite, 
                    extrato=extrato, 
                    numero_saques=numero_saques, 
                    LIMITE_SAQUES=LIMITE_SAQUES
                )
        
        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "nc":
            conta = nova_conta(AGENCIA, usuarios, contas)

        
        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "nu":
            novo_usuario(usuarios)
            
        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a opção desejada.")

main()