import pygame
from a_star import AStar

class AgenteBarbie:
    def __init__(self, pos_inicial, mapa):
        self.posicao = tuple(pos_inicial)  # Converta para tupla
        self.mapa = mapa
        self.amigos_convencidos = 0
        self.amigos = [(5, 5), (10, 10), (15, 15)]  # Posições dos amigos a serem convencidos
        self.caminho_atual = []
        self.a_star = AStar(mapa)

    def atualizar(self):
        if self.amigos_convencidos < 3:
            amigo = self.amigos[self.amigos_convencidos]
            if not self.caminho_atual or self.posicao == self.caminho_atual[-1]:
                self.caminho_atual = self.a_star.encontrar_caminho(self.posicao, amigo)
                if self.caminho_atual:
                    self.caminho_atual.pop(0)  # Remover a posição atual do caminho

            if self.caminho_atual:
                self.posicao = self.caminho_atual.pop(0)

        if self.posicao in self.amigos:
            self.amigos_convencidos += 1
            print(f"Amigo convencido! Total: {self.amigos_convencidos}")

    def desenhar(self, screen):
        x, y = self.posicao
        pygame.draw.rect(screen, (255, 192, 203), pygame.Rect(y * 24, x * 24, 24, 24))  # Barbie
