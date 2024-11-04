import pygame
import sys
import random
from heapq import heappop, heappush
import time

# Inicializando o pygame
pygame.init()

# Cores para cada tipo de terreno e amigos
MAPA_CORES = {
    1: (105, 105, 105),      # Asfalto - Cinza escuro
    3: (139, 69, 19),        # Terra - Marrom
    5: (34, 139, 34),        # Grama - Verde
    10: (169, 169, 169),     # Paralelepípedo - Cinza claro
    99: (255, 140, 0),       # Edifícios - Laranja
    'amigo': (255, 215, 0),  # Amarelo para amigos (não será usado mais)
}

# Tamanho de cada célula no mapa
TAMANHO_CELULA = 24
ATRASO_MOVIMENTO = 10  # Atraso de movimento em milissegundos

# Função para carregar o mapa de um arquivo .txt
def carregar_mapa(arquivo):
    mapa = []
    with open(arquivo, 'r') as f:
        for linha in f:
            mapa.append([int(valor) for valor in linha.split()])
    return mapa

# Carregando o mapa a partir do arquivo txt
MAPA_BARBIE = carregar_mapa('mapa2.txt')

# Configurações da tela
LINHAS_MAPA = len(MAPA_BARBIE)
COLUNAS_MAPA = len(MAPA_BARBIE[0])
LARGURA_JANELA = COLUNAS_MAPA * TAMANHO_CELULA
ALTURA_JANELA = LINHAS_MAPA * TAMANHO_CELULA

# Inicializando a Barbie na posição [22, 18]
POSICAO_BARBIE = [23, 19]

IMAGEM_BARBIE = pygame.image.load('image/barbie.png')
IMAGEM_BARBIE = pygame.transform.scale(IMAGEM_BARBIE, (TAMANHO_CELULA, TAMANHO_CELULA))  # Redimensiona a imagem para caber na célula

# Carregar imagens dos amigos
IMAGENS_AMIGOS = {}
NUM_AMIGOS = 6  # Número total de amigos disponíveis

for i in range(1, NUM_AMIGOS + 1):
    IMAGENS_AMIGOS[f'amigo{i}'] = pygame.image.load(f'image/amigo{i}.png')
    IMAGENS_AMIGOS[f'amigo{i}'] = pygame.transform.scale(IMAGENS_AMIGOS[f'amigo{i}'], (TAMANHO_CELULA, TAMANHO_CELULA))

# Posições dos amigos da Barbie
POSICOES_AMIGOS = [
    (5, 13),
    (10, 9),
    (6, 35),
    (24, 38),
    (36, 15),
    (37, 37)
]

# Garantir que sempre teremos 3 amigos aceitando
respostas_amigos = {}
amigos_aceitos = random.sample(POSICOES_AMIGOS, 3)  # Escolhe 3 amigos aleatoriamente para aceitar

for amigo in POSICOES_AMIGOS:
    respostas_amigos[amigo] = amigo in amigos_aceitos  # Define quem aceitou o convite

tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
pygame.display.set_caption("Mundo da Barbie")

# Classe Agente para Barbie
class AgenteBarbie:
    def __init__(self, pos_inicial):
        self.posicao = pos_inicial
        self.custo_total = 0
        self.amigos_convencidos = 0
        self.rota = []
        self.retornando = False
        self.caminho = []  # Lista para armazenar o caminho percorrido

    def mover(self):
        if self.rota:
            nova_posicao = self.rota.pop(0)
            custo = MAPA_BARBIE[nova_posicao[0]][nova_posicao[1]]
            if custo == 99:  # Edifício
                print("Movimento bloqueado: edifício")
                return False

            # Verifica se a nova posição é a de um amigo
            if tuple(nova_posicao) in respostas_amigos:
                if respostas_amigos[tuple(nova_posicao)]:
                    respostas_amigos.pop(tuple(nova_posicao))  # Remove amigo convencido
                    self.amigos_convencidos += 1
                    print(f"Amigo convencido! Total de amigos convencidos: {self.amigos_convencidos}")

                    # Atualiza a lista de amigos visíveis
                    amigos_visiveis.remove(tuple(nova_posicao))

                    # Quando pegar o terceiro amigo, iniciar retorno ao início
                    if self.amigos_convencidos == 3:
                        self.retornando = True
                        self.rota = self.calcular_rota(POSICAO_BARBIE)
                else:
                    print("Amigo recusou o convite. Procurando outro amigo.")
                    respostas_amigos.pop(tuple(nova_posicao))  # Remove o amigo que recusou
                    self.procurar_proximo_amigo()
                    return  # Impede que a Barbie mude a posição se o amigo recusou

            self.posicao = nova_posicao
            self.caminho.append(nova_posicao)  # Adiciona nova posição ao caminho
            self.custo_total += custo
            print(f"Movendo para {nova_posicao}, custo: {custo}. Custo total: {self.custo_total}")

            # Calcular e exibir o tempo total
            tempo_total = time.time() - inicio_tempo
            print(f"Tempo total de execução: {tempo_total:.2f} segundos")

            # Verifica se voltou ao ponto inicial após pegar três amigos
            if self.retornando and self.posicao == POSICAO_BARBIE:
                print(f"Barbie retornou ao ponto inicial. Custo final total: {self.custo_total}")
                pygame.quit()
                sys.exit()
            return True
        return False

    def procurar_proximo_amigo(self):
        proximo_amigo = amigo_mais_proximo(self.posicao, respostas_amigos.keys())
        if proximo_amigo:
            self.rota = self.calcular_rota(proximo_amigo)
        else:
            print("Não há mais amigos disponíveis.")

    def calcular_rota(self, destino):
        inicio = tuple(self.posicao)
        fim = tuple(destino)

        conjunto_aberto = []
        heappush(conjunto_aberto, (0, inicio))
        veio_de = {}
        g_score = {inicio: 0}
        f_score = {inicio: self.heuristica(inicio, fim)}

        while conjunto_aberto:
            atual = heappop(conjunto_aberto)[1]

            if atual == fim:
                return self.reconstruir_caminho(veio_de, atual)

            for vizinho in self.get_vizinhos(atual):
                g_tentativa = g_score[atual] + MAPA_BARBIE[vizinho[0]][vizinho[1]]
                if vizinho not in g_score or g_tentativa < g_score[vizinho]:
                    veio_de[vizinho] = atual
                    g_score[vizinho] = g_tentativa
                    f_score[vizinho] = g_tentativa + self.heuristica(vizinho, fim)
                    if vizinho not in [i[1] for i in conjunto_aberto]:
                        heappush(conjunto_aberto, (f_score[vizinho], vizinho))

        return []

    def heuristica(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Distância Manhattan

    def get_vizinhos(self, pos):
        vizinhos = []
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Cima, Baixo, Esquerda, Direita
            vizinho = (pos[0] + d[0], pos[1] + d[1])
            if 0 <= vizinho[0] < LINHAS_MAPA and 0 <= vizinho[1] < COLUNAS_MAPA:
                if MAPA_BARBIE[vizinho[0]][vizinho[1]] != 99:  # Não é um edifício
                    vizinhos.append(vizinho)
        return vizinhos

    def reconstruir_caminho(self, veio_de, atual):
        caminho_total = [atual]
        while atual in veio_de:
            atual = veio_de[atual]
            caminho_total.append(atual)
        caminho_total.reverse()
        return caminho_total

# Função para encontrar o amigo mais próximo da Barbie
def amigo_mais_proximo(pos_barbie, amigos):
    menor_distancia = float('inf')
    amigo_mais_prox = None
    for amigo in amigos:
        distancia = abs(pos_barbie[0] - amigo[0]) + abs(pos_barbie[1] - amigo[1])  # Distância de Manhattan
        if distancia < menor_distancia:
            menor_distancia = distancia
            amigo_mais_prox = amigo
    return amigo_mais_prox

# Função para desenhar a grade
def desenhar_grade(tela):
    for i in range(0, LARGURA_JANELA, TAMANHO_CELULA):
        pygame.draw.line(tela, (200, 200, 200), (i, 0), (i, ALTURA_JANELA))  # Linhas verticais
    for j in range(0, ALTURA_JANELA, TAMANHO_CELULA):
        pygame.draw.line(tela, (200, 200, 200), (0, j), (LARGURA_JANELA, j))  # Linhas horizontais

def desenhar_mapa(tela, agente, amigos):
    for i in range(len(MAPA_BARBIE)):
        for j in range(len(MAPA_BARBIE[i])):
            custo = MAPA_BARBIE[i][j]
            cor = MAPA_CORES.get(custo, (0, 0, 0))
            pygame.draw.rect(tela, cor, pygame.Rect(j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    
    # Desenhar os amigos usando suas imagens
    for pos_amigo in amigos:
        indice_amigo = POSICOES_AMIGOS.index(pos_amigo) + 1  # +1 para corresponder ao índice das imagens
        imagem_amigo = IMAGENS_AMIGOS[f'amigo{indice_amigo}']
        tela.blit(imagem_amigo, (pos_amigo[1] * TAMANHO_CELULA, pos_amigo[0] * TAMANHO_CELULA))

    # Desenhar o caminho percorrido pela Barbie
    for pos in agente.caminho:
        pygame.draw.rect(tela, (255, 182, 193), pygame.Rect(pos[1] * TAMANHO_CELULA, pos[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))  # Rosa claro para o caminho

    # Desenhar a posição da Barbie usando a imagem
    x, y = agente.posicao
    tela.blit(IMAGEM_BARBIE, (y * TAMANHO_CELULA, x * TAMANHO_CELULA))

# Inicialização da Barbie e amigos
barbie = AgenteBarbie(POSICAO_BARBIE[:])
amigos_visiveis = POSICOES_AMIGOS[:]  # Lista para manter amigos visíveis

# Loop principal
inicio_tempo = time.time()  # Marca o tempo de início
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Se a Barbie não tiver rota e não estiver retornando, ela busca o próximo amigo mais próximo
    if not barbie.rota and not barbie.retornando:
        barbie.procurar_proximo_amigo()

    # Mover a Barbie
    barbie.mover()

    # Desenha o mapa, a grade, a Barbie e os amigos
    tela.fill((0, 0, 0))  # Limpa a tela
    desenhar_mapa(tela, barbie, amigos_visiveis)  # Mantenha amigos visíveis
    desenhar_grade(tela)
    pygame.display.flip()

    # Controla a velocidade de movimento
    pygame.time.delay(ATRASO_MOVIMENTO)

pygame.quit()
sys.exit()
