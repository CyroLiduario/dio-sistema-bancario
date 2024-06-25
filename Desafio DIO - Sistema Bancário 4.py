# Sistema bancário seguindo o paradigma de classes.
# * - todos os argumentos após a * são nomeados
# / - todos os argumentos antes do / são posicionais
import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

def verificar_decimal(numero):
    decimal = numero.split('.')[1]
    if len(decimal) > 2:
        print('ERRO: Valor inválido, por favor insira um valor com até duas casas decimais.')
        return False
    
    else:
        return True

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
    def __init__(self, numero, cliente, AGENCIA="0001"):
        self._numero = numero
        self._agencia = AGENCIA
        self._cliente = cliente
        self._saldo = 0
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, cliente, AGENCIA="0001"):
        return cls(numero, cliente, AGENCIA)    

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
        saldo = self.saldo
        if saldo <= 0:
            print("ERRO: Você não possui saldo em conta.")
            return False
        
        else:
            if valor <= 0:
                print('ERRO: Valor inválido, por favor informe um valor acima de zero.')
                return False
            
            if valor > saldo:
                print(f'ERRO: Saldo insuficiente.')
                return False
            
            else:
                self._saldo -= valor   
                print("Saque realizado com sucesso!")
                return True

    def depositar(self, valor):
        saldo = self.saldo
       
        if valor <= 0:
            print('ERRO: Valor inválido, por favor informe um valor acima de zero.')
            return False
        else:
            self._saldo += valor
            print('Depósito realizado com sucesso!')
            return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, AGENCIA="0001", limite=500, limite_de_saques=3):
        super().__init__(numero, cliente, AGENCIA)
        self.limite = limite
        self.limite_de_saques = limite_de_saques

    def sacar(self, valor):
        numero_de_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["Tipo"] == Saque.__name__]
        )

        if numero_de_saques > self.limite_de_saques:
            print("ERRO: Você já atingiu o limite diário de saques")
            return False
        
        elif valor > self.limite:
            print(f'ERRO: O valor informado de R$ {valor:.2f} está acima do seu limite de R$ {self.limite:.2f} por saque. Por favor, informe um valor válido.')
            return False
        
        else:
            return super().sacar(valor)

    def __str__(self):
        return f"""\n
            Agência:\t{self.agencia}\n
            C/C:\t{self.numero}\n
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "Tipo" : transacao.__class__.__name__,
                "Valor" : transacao.valor,
                "Data" : datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )

class Transacao(ABC):
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)
    
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

def deposito(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_usuario(cpf, clientes)
    if not cliente:
        print('ERRO: Cliente não encontrado')
        return

    str_valor_deposito = input('Informe o valor do depósito ou digite "c" para cancelar: ')
    if str_valor_deposito == "c":
        return
    
    valor_deposito = float(str_valor_deposito)
    transacao = Deposito(valor_deposito)
    
    conta = recuperar_conta(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def saque(clientes):
    cpf = input("Informe o CPF do cliente:")
    cliente = filtrar_usuario(cpf, clientes)
    if not cliente:
        print('ERRO: Cliente não encontrado')
        return

    str_valor_saque = input('Informe o valor do saque ou digite "c" para cancelar: ')
    if str_valor_saque == "c":
        return
    
    valor = float(str_valor_saque)
    transacao = Saque(valor)
    
    conta = recuperar_conta(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_usuario(cpf, clientes)
    if not cliente:
        print('ERRO: Cliente não encontrado')
        return
    
    conta = recuperar_conta(cliente)
    if not conta:
        return
    print("\n══════════════ Extrato ══════════════")
    print(f"\nSaldo:\t\tR$ {conta.saldo:.2f}")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações"
    
    else:
        for transacao in transacoes:
            extrato += f'\n{transacao["Data"]}\t{transacao["Tipo"]}\tR${transacao["Valor"]:.2f}'
    
    print(extrato)
    print("\n═════════════════════════════════════")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta(cliente):
    if not cliente.contas:
        print('ERRO: Cliente não possui contas.')
        return
    
    # print('O cliente possui as seguintes contas:')
    # print(f''' {
    #                 [ conta.numero for conta in cliente.contas ]
    #             }
    #         ''')
    # input('Qual conta deseja acessar?')
    return cliente.contas[0]

def novo_usuario(usuarios):
    cpf = input('Insira seu CPF (apenas números): ')
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("\n ERRO: Este CPF já está vinculado a um usuário.")
        return
    
    nome = input("Nome completo: ")
    data_de_nascimento = input("Data de Nascimento (DD-MM-AAAA): ")
    endereco = input("Endereço (Logradouro, Número - Bairro - Cidade/UF): ")
    cliente = PessoaFisica(
        cpf=cpf,
        nome=nome,
        data_de_nascimento=data_de_nascimento,
        endereco=endereco
    )
    usuarios.append(cliente)
    print('Usuário criado com sucesso!')

def nova_conta(usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)
    numero_da_conta = len(contas) + 1
    
    if not usuario:
        print('ERRO: Usuário não encontrado. Por favor, cadastre novo usuário antes de abrir uma nova conta.')
        return
    
    print('Conta criada com sucesso!')
    conta = ContaCorrente.nova_conta(
        cliente=usuario,
        numero=numero_da_conta
    )

    contas.append(conta)
    usuario.contas.append(conta)

def listar_contas(contas):
    for conta in contas:
        print('═' * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []
    
    while True:

        opcao = menu()

        if opcao == "d":
            deposito(clientes)

        elif opcao == "s":
            saque(clientes)
        
        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nc":
            conta = nova_conta(clientes, contas)

        
        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "nu":
            novo_usuario(clientes)
            
        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a opção desejada.")

main()