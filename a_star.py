class AStar:
    def __init__(self, mapa):
        self.mapa = mapa

    def heuristica(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Distância Manhattan

    def encontrar_caminho(self, inicio, fim):
        open_set = {inicio}
        closed_set = set()
        came_from = {}
        g_score = {inicio: 0}
        f_score = {inicio: self.heuristica(inicio, fim)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))

            if current == fim:
                return self.reconstruir_caminho(came_from, current)

            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self.vizinhos(current):
                if neighbor in closed_set or self.mapa[neighbor[0]][neighbor[1]] == 99:  # Não pode passar
                    continue

                tentative_g_score = g_score[current] + 1  # Custo fixo para cada movimento

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristica(neighbor, fim)

                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return []  # Caminho não encontrado

    def vizinhos(self, pos):
        direcoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        vizinhos = []
        for d in direcoes:
            neighbor = (pos[0] + d[0], pos[1] + d[1])
            if 0 <= neighbor[0] < len(self.mapa) and 0 <= neighbor[1] < len(self.mapa[0]):
                vizinhos.append(neighbor)
        return vizinhos

    def reconstruir_caminho(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path
