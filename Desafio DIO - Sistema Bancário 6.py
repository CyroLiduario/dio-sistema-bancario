# Sistema bancário seguindo o paradigma de classes.
# FIXME: a função listar contas está mostrando saldos desatualizados.

import os
import pickle
import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime, timezone
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

import inquirer

ROOT_PATH = Path(__file__).parent


def load_contas():
    if os.path.exists(ROOT_PATH / "contas.pk1"):
        with open(ROOT_PATH / "contas.pk1", "rb") as instancias_contas:
            return pickle.load(instancias_contas)
    else:
        return []


def load_clientes():
    if os.path.exists(ROOT_PATH / "clientes.pk1"):
        with open(ROOT_PATH / "clientes.pk1", "rb") as instancias_clientes:
            return pickle.load(instancias_clientes)
    else:
        return []


def salvar_contas(contas):
    with open(ROOT_PATH / "contas.pk1", "wb") as instancias_contas:
        return pickle.dump(contas, instancias_contas)


def salvar_clientes(clientes):
    with open(ROOT_PATH / "clientes.pk1", "wb") as instancias_clientes:
        return pickle.dump(clientes, instancias_clientes)


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{datetime.now()}: {func.__name__.upper()}")
        with open(ROOT_PATH / "log.txt", "a") as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__.upper()}' executada com argumentos {args} e {kwargs}."
                "Retornou {resultado}\n"
            )
        return resultado

    return envelope


def verificar_decimal(numero):
    decimal = numero.split(".")[1]
    if len(decimal) > 2:
        print(
            "ERRO: Valor inválido, por favor insira um valor com até duas casas decimais."
        )
        return False

    else:
        return True


class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""
                Agência:\t{conta.agencia}
                Número:\t\t{conta.numero}
                Titular:\t{conta.cliente.nome}
                Saldo:\t\tR$ {conta.saldo:.2f}
            """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Cliente:
    def __init__(self, endereco: str, senha: str):
        self.endereco = endereco
        self.contas = []
        self._senha = self._gerar_senha(senha)

    def _gerar_senha(self, senha):
        return generate_password_hash(senha)
    
    def _checar_senha(self, senha):
        return check_password_hash(self._senha, senha)
    
    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("ERRO: Número de transações diárias excedido!")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_de_nascimento, endereco, senha):
        self.cpf = cpf
        self.nome = nome
        self.data_de_nascimento = data_de_nascimento
        super().__init__(endereco, senha)

    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.nome}', '{self.cpf}')>"


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
                print("ERRO: Valor inválido, por favor informe um valor acima de zero.")
                return False

            if valor > saldo:
                print("ERRO: Saldo insuficiente.")
                return False

            else:
                self._saldo -= valor
                print("Saque realizado com sucesso!")
                return True

    def depositar(self, valor):

        if valor <= 0:
            print("ERRO: Valor inválido, por favor informe um valor acima de zero.")
            return False
        else:
            self._saldo += valor
            print("Depósito realizado com sucesso!")
            return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, AGENCIA="0001", limite=500, limite_de_saques=3):
        super().__init__(numero, cliente, AGENCIA)
        self.limite = limite
        self.limite_de_saques = limite_de_saques

    def sacar(self, valor):
        numero_de_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["Tipo"] == Saque.__name__
            ]
        )

        if numero_de_saques > self.limite_de_saques:
            print("ERRO: Você já atingiu o limite diário de saques")
            return False

        elif valor > self.limite:
            print(
                f"ERRO: O valor informado de R$ {valor:.2f} está acima do seu limite de R$ {self.limite:.2f} por saque."
                "Por favor, informe um valor válido."
            )
            return False

        else:
            return super().sacar(valor)

    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

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
                "Tipo": transacao.__class__.__name__,
                "Valor": transacao.valor,
                "Data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_de_transacao=None):
        for transacao in self._transacoes:
            if (
                tipo_de_transacao is None
                or transacao["Tipo"].lower() == tipo_de_transacao.lower()
            ):
                yield transacao

    def transacoes_do_dia(self):
        transacoes = []
        for transacao in self._transacoes:
            if (
                datetime.strptime(transacao["Data"], "%d-%m-%Y %H:%M:%S").date()
                == datetime.now(timezone.utc).date()
            ):
                transacoes.append(transacao)
        return transacoes


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

class Session:
    def __init__(self, cliente, conta):
        self.cliente = cliente
        self.conta = conta
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.cliente}', '{self.conta.numero}')>"

def login(clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_usuario(cpf, clientes)
    if not cliente:
        print("ERRO: Cliente não encontrado")
        return None

    senha = input("Informe a senha: ")
    if not cliente._checar_senha(senha):
        print("ERRO: Senha incorreta")
        return None

    conta = recuperar_conta(cliente)
    if not conta:
        opcao = input("O cliente ainda não possui contas ativas, deseja criar uma nova? [Y / N] \n► ")
        if opcao == "N":
            print("Operação cancelada pelo usuário!")
            return None
        elif opcao == "Y":
            conta = nova_conta(
                cliente=cliente,
                contas=contas
            )

    print("Login realizado com sucesso!")
    return Session(cliente, conta)

def menu():

    menu = """
    ══════════════ MENU ══════════════
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tListar Contas
    [lg]\tLogoff
    [q]\tSair
    ► """
    return input(textwrap.dedent(menu))

def menu_start():

    menu = """
    ══════════════ MENU ══════════════
    [lg]\tLogin
    [nu]\tNovo Usuário
    [q]\tSair
    ► """
    return input(textwrap.dedent(menu))

@log_transacao
def deposito(session):
    cliente = session.cliente
    conta = session.conta

    str_valor_deposito = input(
        'Informe o valor do depósito ou digite "c" para cancelar: '
    )
    if str_valor_deposito == "c":
        return

    valor_deposito = float(str_valor_deposito)
    transacao = Deposito(valor_deposito)

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def saque(session):
    cliente = session.cliente
    conta = session.conta

    str_valor_saque = input('Informe o valor do saque ou digite "c" para cancelar: ')
    if str_valor_saque == "c":
        return

    valor = float(str_valor_saque)
    transacao = Saque(valor)

    cliente.realizar_transacao(conta, transacao)
    return True


@log_transacao
def exibir_extrato(session):
    conta = session.conta

    print("\n════════════════════════ Extrato ════════════════════════")
    print(f"\nSaldo:\t\tR$ {conta.saldo:.2f}")
    transacoes = False

    extrato = ""
    for transacao in conta.historico.gerar_relatorio():
        extrato += f'\n{transacao["Data"]}\t{transacao["Tipo"]:<15}\tR${transacao["Valor"]:.2f}'
        transacoes = True

    if not transacoes:
        extrato = "Não foram realizadas movimentações"

    print(textwrap.dedent(extrato))
    print("\n═════════════════════════════════════════════════════════")


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def recuperar_conta(cliente):
    if not cliente.contas:
        print("ERRO: Cliente não possui contas.")
        return

    contas = [(conta.numero, conta) for conta in cliente.contas]
    numero_das_contas = [conta.numero for conta in cliente.contas]
    if len(numero_das_contas) == 1:
        print(
            f"Apenas uma conta foi encontrada. Conta {numero_das_contas[0]} selecionada!"
        )
        return cliente.contas[0]
    seletor = [
        inquirer.List(
            "numero_da_conta",
            message="Selecione a conta desejada",
            choices=numero_das_contas,
            carousel=True,
        )
    ]
    selecao = inquirer.prompt(seletor)
    conta_selecionada = next(
        conta for numero, conta in contas if numero == selecao["numero_da_conta"]
    )
    return conta_selecionada


@log_transacao
def novo_usuario(usuarios):
    cpf = input("Insira seu CPF (apenas números): ")
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("\n ERRO: Este CPF já está vinculado a um usuário.")
        return

    nome = input("Nome completo: ")
    data_de_nascimento = input("Data de Nascimento (DD-MM-AAAA): ")
    endereco = input("Endereço (Logradouro, Número - Bairro - Cidade/UF): ")
    senha = input("Senha: ")
    cliente = PessoaFisica(
        cpf=cpf, nome=nome, data_de_nascimento=data_de_nascimento, endereco=endereco, senha=senha
    )
    usuarios.append(cliente)
    print("Usuário criado com sucesso!")


@log_transacao
def nova_conta(contas, session=None, cliente=None):
    if session is None:
        usuario = cliente
    else:
        usuario = session.cliente
    
    numero_da_conta = len(contas) + 1

    print("Conta criada com sucesso!")
    conta = ContaCorrente.nova_conta(cliente=usuario, numero=numero_da_conta)

    contas.append(conta)
    usuario.contas.append(conta)


def listar_contas(contas, session):
    contas_usuario = [ conta for conta in contas if conta.cliente.cpf == session.cliente.cpf]

    if not contas_usuario:
        print("O usuário não possui contas cadastradas.")
        return
    for conta in ContasIterador(contas_usuario):
        print("═" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    session = None
    clientes = load_clientes()
    contas = load_contas()

    while True:
        if session is None:
            opcao = menu_start()
            if opcao == "lg":
                session = login(clientes, contas)

            elif opcao == "nu":
                novo_usuario(clientes)
            
            elif opcao == "q":
                salvar_clientes(clientes)
                salvar_contas(contas)
                break

            else:
                print("Operação inválida, por favor selecione novamente a opção desejada.")

        else:
            opcao = menu()
        
            if opcao == "d":
                deposito(session)

            elif opcao == "s":
                sacar = False
                while sacar is False:
                    sacar = saque(session)

            elif opcao == "e":
                exibir_extrato(session)

            elif opcao == "nc":
                nova_conta(session=session, contas=contas)

            elif opcao == "lc":
                listar_contas(contas, session)

            elif opcao == "lg":
                session = None

            elif opcao == "q":
                salvar_clientes(clientes)
                salvar_contas(contas)
                break

            else:
                print("Operação inválida, por favor selecione novamente a opção desejada.")


main()
