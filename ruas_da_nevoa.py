import pygame
import sys
import random
import math
import io

# ===================== CONFIGURAÇÕES GERAIS =====================
pygame.init()

LARGURA, ALTURA = 1200, 750
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("RUAS DA NÉVOA — Terror Estilo Silent Hill")

# Cores temáticas
PRETO = (0, 0, 0)
CINZA_ESCURO = (22, 22, 28)
CINZA_RUA = (45, 48, 55)
CINZA_NÉVOA = (100, 105, 115)
VERMELHO = (190, 30, 30)
VERMELHO_FRACO = (90, 20, 20)
BRANCO = (210, 210, 215)
AMARELO = (230, 190, 30)
VERDE = (35, 190, 65)
VERDE_ESCURO = (25, 120, 45)
MARROM = (90, 60, 30)
AZUL = (40, 130, 220)
ROXO_ESCURO = (60, 40, 80)
CINZA_PAREDE = (70, 75, 85)

relogio = pygame.time.Clock()
FPS = 60
FONTE_PEQUENA = pygame.font.SysFont("Arial", 14)
FONTE_MEDIA = pygame.font.SysFont("Arial", 22)
FONTE_GRANDE = pygame.font.SysFont("Arial", 36)

MAPA_LARGURA = 2400
MAPA_ALTURA = 1600

# ===================== FUNÇÃO AUXILIAR: CRIAR SPRITES DOS DADOS =====================
def criar_sprite_de_pixels(dados_pixels, tamanho_final=32):
    """Cria uma superfície Pygame a partir de matriz de cores"""
    altura_sprite = len(dados_pixels)
    largura_sprite = len(dados_pixels[0]) if altura_sprite > 0 else 0
    sup = pygame.Surface([largura_sprite, altura_sprite], pygame.SRCALPHA)
    for y, linha in enumerate(dados_pixels):
        for x, cor in enumerate(linha):
            if cor:
                sup.set_at((x, y), cor)
    return pygame.transform.scale(sup, (tamanho_final, tamanho_final))

# ===================== SPRITE DO JOGADOR =====================
# Pixel art do personagem (primeira imagem)
COR_TRANSPARENTE = None
jogador_pixels = [
    [None, None, (30, 20, 15), (30, 20, 15), (30, 20, 15), (30, 20, 15), None, None],
    [None, (30, 20, 15), (210, 180, 150), (210, 180, 150), (210, 180, 150), (210, 180, 150), (30, 20, 15), None],
    [(30, 20, 15), (210, 180, 150), (50, 40, 35), (210, 180, 150), (210, 180, 150), (50, 40, 35), (210, 180, 150), (30, 20, 15)],
    [(30, 20, 15), (210, 180, 150), (210, 180, 150), (210, 180, 150), (210, 180, 150), (210, 180, 150), (210, 180, 150), (30, 20, 15)],
    [None, (30, 20, 15), (140, 50, 70), (140, 50, 70), (140, 50, 70), (140, 50, 70), (30, 20, 15), None],
    [None, None, (140, 50, 70), (140, 50, 70), (140, 50, 70), (140, 50, 70), None, None],
    [None, None, (40, 40, 45), (40, 40, 45), (40, 40, 45), (40, 40, 45), None, None],
    [None, (40, 40, 45), (40, 40, 45), (70, 60, 55), (70, 60, 55), (40, 40, 45), (40, 40, 45), None],
    [None, None, (40, 40, 45), (40, 40, 45), (40, 40, 45), (40, 40, 45), None, None],
]
sprite_jogador = criar_sprite_de_pixels(jogador_pixels, 36)

# ===================== SPRITE DO INIMIGO =====================
# Pixel art do monstro (segunda imagem — simplificado com as características principais)
inimigo_pixels = [
    [None, None, (70, 25, 25), (90, 30, 30), (90, 30, 30), (70, 25, 25), None, None],
    [None, (70, 25, 25), (110, 35, 35), (130, 40, 40), (130, 40, 40), (110, 35, 35), (70, 25, 25), None],
    [(70, 25, 25), (110, 35, 35), (150, 45, 45), (170, 55, 55), (170, 55, 55), (150, 45, 45), (110, 35, 35), (70, 25, 25)],
    [(90, 30, 30), (130, 40, 40), (190, 65, 65), (200, 75, 75), (200, 75, 75), (190, 65, 65), (130, 40, 40), (90, 30, 30)],
    [(90, 30, 30), (130, 40, 40), (200, 75, 75), (210, 85, 85), (210, 85, 85), (200, 75, 75), (130, 40, 40), (90, 30, 30)],
    [(70, 25, 25), (110, 35, 35), (190, 65, 65), (200, 75, 75), (200, 75, 75), (190, 65, 65), (110, 35, 35), (70, 25, 25)],
    [None, (70, 25, 25), (150, 45, 45), (170, 55, 55), (170, 55, 55), (150, 45, 45), (70, 25, 25), None],
    [None, None, (70, 25, 25), (90, 30, 30), (90, 30, 30), (70, 25, 25), None, None],
]
sprite_inimigo = criar_sprite_de_pixels(inimigo_pixels, 40)

# ===================== CLASSES =====================

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = sprite_jogador.copy()
        self.rect = self.image.get_rect(center=(MAPA_LARGURA//2, MAPA_ALTURA//2))
        self.velocidade = 3.8
        self.vida = 100
        self.vida_max = 100
        self.pontos = 0
        self.imunidade = 0
        self.angulo = 0

        self.armas = {
            "faca": {"dano": 18, "alcance": 55, "cooldown": 350, "tipo": "branca", "munição": float('inf')},
            "cacetete": {"dano": 28, "alcance": 65, "cooldown": 500, "tipo": "branca", "munição": float('inf')},
            "pistola": {"dano": 40, "alcance": 400, "cooldown": 300, "tipo": "fogo", "munição": float('inf')},
            "espingarda": {"dano": 75, "alcance": 280, "cooldown": 700, "tipo": "fogo", "munição": float('inf')}
        }
        self.arma_atual = "faca"
        self.tempo_ataque = 0
        self.ataque_ativo = None

    def mover(self, teclas, obstaculos):
        dx, dy = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]: dy -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dx -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx += 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        novo_x = self.rect.x + dx * self.velocidade
        novo_y = self.rect.y + dy * self.velocidade

        rect_teste_x = self.rect.copy()
        rect_teste_x.x = novo_x
        if not rect_teste_x.collidelistall(obstaculos):
            self.rect.x = novo_x

        rect_teste_y = self.rect.copy()
        rect_teste_y.y = novo_y
        if not rect_teste_y.collidelistall(obstaculos):
            self.rect.y = novo_y

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > MAPA_LARGURA: self.rect.right = MAPA_LARGURA
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > MAPA_ALTURA: self.rect.bottom = MAPA_ALTURA

    def atualizar_angulo(self, pos_mouse, camera):
        mouse_mapa_x = pos_mouse[0] + camera.x
        mouse_mapa_y = pos_mouse[1] + camera.y
        dx = mouse_mapa_x - self.rect.centerx
        dy = mouse_mapa_y - self.rect.centery
        self.angulo = math.degrees(math.atan2(dy, dx))

    def atacar(self, pos_mouse, camera):
        agora = pygame.time.get_ticks()
        arma = self.armas[self.arma_atual]
        if agora - self.tempo_ataque < arma["cooldown"]:
            return None
        self.tempo_ataque = agora

        mouse_mapa_x = pos_mouse[0] + camera.x
        mouse_mapa_y = pos_mouse[1] + camera.y

        if arma["tipo"] == "fogo":
            dx = mouse_mapa_x - self.rect.centerx
            dy = mouse_mapa_y - self.rect.centery
            dist = math.hypot(dx, dy) or 1
            dx, dy = dx/dist, dy/dist
            self.ataque_ativo = {"tipo": "tiro", "dx": dx, "dy": dy, "dano": arma["dano"],
                                 "alcance": arma["alcance"], "inicio": pygame.time.get_ticks()}
            return self.ataque_ativo
        else:
            self.ataque_ativo = {"tipo": "corpo_a_corpo", "dano": arma["dano"],
                                 "alcance": arma["alcance"], "angulo": self.angulo,
                                 "inicio": pygame.time.get_ticks()}
            return self.ataque_ativo

    def trocar_arma(self, nome):
        if nome in self.armas:
            self.arma_atual = nome

    def tomar_dano(self, quantidade):
        if pygame.time.get_ticks() - self.imunidade > 800:
            self.vida -= quantidade
            self.imunidade = pygame.time.get_ticks()
            return True
        return False

    def curar(self, qtd):
        self.vida = min(self.vida_max, self.vida + qtd)

    def update(self):
        if self.ataque_ativo and pygame.time.get_ticks() - self.ataque_ativo["inicio"] > 200:
            self.ataque_ativo = None


class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, nivel=1):
        super().__init__()
        self.image = sprite_inimigo.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.velocidade = 1.5 * (1 + nivel*0.1)
        self.vida = 50 * (1 + nivel*0.15)
        self.vida_max = self.vida
        self.dano = 15
        self.pontos_valor = 150
        self.ultimo_ataque = 0

    def seguir_jogador(self, jogador, obstaculos):
        dx = jogador.rect.centerx - self.rect.centerx
        dy = jogador.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1

        if dist > 35:
            novo_x = self.rect.x + (dx/dist) * self.velocidade
            novo_y = self.rect.y + (dy/dist) * self.velocidade

            rect_teste = pygame.Rect(novo_x, self.rect.y, self.rect.width, self.rect.height)
            if not rect_teste.collidelistall(obstaculos):
                self.rect.x = novo_x

            rect_teste = pygame.Rect(self.rect.x, novo_y, self.rect.width, self.rect.height)
            if not rect_teste.collidelistall(obstaculos):
                self.rect.y = novo_y

        if dist < 40 and pygame.time.get_ticks() - self.ultimo_ataque > 1000:
            if jogador.tomar_dano(self.dano):
                self.ultimo_ataque = pygame.time.get_ticks()
                return True
        return False

    def tomar_dano(self, qtd):
        self.vida -= qtd
        return self.vida <= 0


class Item(pygame.sprite.Sprite):
    def __init__(self, tipo, x, y):
        super().__init__()
        self.tipo = tipo
        cores = {"vida": VERDE, "munição": AMARELO}
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.rect(self.image, cores[tipo], (2, 2, 16, 16), border_radius=4)
        self.rect = self.image.get_rect(center=(x, y))

    def coletar(self, jogador):
        if self.tipo == "vida":
            jogador.curar(25)
        return True


class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, largura, altura):
        super().__init__()
        self.tipo = tipo
        self.rect = pygame.Rect(x, y, largura, altura)
        self.image = pygame.Surface([largura, altura], pygame.SRCALPHA)

        if tipo == "arvore":
            pygame.draw.rect(self.image, MARROM, (largura//2 - 6, altura//2, 12, altura//2))
            pygame.draw.circle(self.image, VERDE_ESCURO, (largura//2, altura//3), largura//2)
        elif tipo == "parede":
            pygame.draw.rect(self.image, CINZA_PAREDE, (0, 0, largura, altura))
            pygame.draw.rect(self.image, (55, 60, 70), (2, 2, largura-4, altura-4), 2)

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, dano, alcance):
        super().__init__()
        self.image = pygame.Surface([8, 8], pygame.SRCALPHA)
        pygame.draw.circle(self.image, AMARELO, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx * 12
        self.dy = dy * 12
        self.dano = dano
        self.alcance_restante = alcance

    def update(self, inimigos, obstaculos):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.alcance_restante -= math.hypot(self.dx, self.dy)

        if self.rect.collidelistall(obstaculos):
            return "parede", False, None

        for inimigo in inimigos:
            if self.rect.colliderect(inimigo.rect):
                morto = inimigo.tomar_dano(self.dano)
                return "atingiu", morto, inimigo

        if self.alcance_restante <= 0:
            return "fim", False, None
        return "ativo", False, None

# ===================== FUNÇÕES AUXILIARES =====================

def gerar_mapa():
    obstaculos = pygame.sprite.Group()

    for _ in range(80):
        x = random.randint(100, MAPA_LARGURA - 100)
        y = random.randint(100, MAPA_ALTURA - 100)
        tam = random.choice([40, 50, 60])
        if abs(x - MAPA_LARGURA//2) > 150 or abs(y - MAPA_ALTURA//2) > 150:
            obstaculos.add(Obstaculo(x, y, "arvore", tam, tam))

    obstaculos.add(Obstaculo(0, 0, "parede", MAPA_LARGURA, 40))
    obstaculos.add(Obstaculo(0, MAPA_ALTURA-40, "parede", MAPA_LARGURA, 40))
    obstaculos.add(Obstaculo(0, 0, "parede", 40, MAPA_ALTURA))
    obstaculos.add(Obstaculo(MAPA_LARGURA-40, 0, "parede", 40, MAPA_ALTURA))

    predios = [
        (200, 200, 180, 120), (500, 300, 150, 150),
        (1800, 400, 200, 100), (1600, 1200, 180, 140),
        (800, 1000, 160, 120), (2000, 1300, 150, 150),
        (1000, 200, 200, 80), (300, 1300, 140, 160)
    ]
    for px, py, pw, ph in predios:
        obstaculos.add(Obstaculo(px, py, "parede", pw, ph))

    return obstaculos

def desenhar_fundo_mapa(superficie):
    superficie.fill(CINZA_ESCURO)
    for i in range(0, MAPA_LARGURA, 80):
        pygame.draw.line(superficie, CINZA_RUA, (i, 0), (i, MAPA_ALTURA), 1)
    for i in range(0, MAPA_ALTURA, 80):
        pygame.draw.line(superficie, CINZA_RUA, (0, i), (MAPA_LARGURA, i), 1)

def desenhar_minimapa(jogador, todos_inimigos, obstaculos):
    MM_LARGURA = 200
    MM_ALTURA = 130
    MM_X = LARGURA - MM_LARGURA - 15
    MM_Y = 15

    pygame.draw.rect(tela, (15, 15, 20), (MM_X, MM_Y, MM_LARGURA, MM_ALTURA))
    pygame.draw.rect(tela, (60, 60, 70), (MM_X, MM_Y, MM_LARGURA, MM_ALTURA), 2)

    escala_x = MM_LARGURA / MAPA_LARGURA
    escala_y = MM_ALTURA / MAPA_ALTURA

    for obs in obstaculos:
        rx = MM_X + obs.rect.x * escala_x
        ry = MM_Y + obs.rect.y * escala_y
        rw = obs.rect.width * escala_x
        rh = obs.rect.height * escala_y
        pygame.draw.rect(tela, (50, 55, 65), (rx, ry, rw, rh))

    for ini in todos_inimigos:
        ix = MM_X + ini.rect.centerx * escala_x
        iy = MM_Y + ini.rect.centery * escala_y
        pygame.draw.circle(tela, VERMELHO, (int(ix), int(iy)), 3)

    jx = MM_X + jogador.rect.centerx * escala_x
    jy = MM_Y + jogador.rect.centery * escala_y
    pygame.draw.circle(tela, AZUL, (int(jx), int(jy)), 5)
    pygame.draw.circle(tela, BRANCO, (int(jx), int(jy)), 2)

    tela.blit(FONTE_PEQUENA.render("MINIMAPA", True, BRANCO), (MM_X + 60, MM_Y - 1))

def desenhar_nevoa():
    s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    s.fill((CINZA_NÉVOA[0], CINZA_NÉVOA[1], CINZA_NÉVOA[2], 55))
    tela.blit(s, (0, 0))

def desenhar_interface(jogador, onda):
    pygame.draw.rect(tela, VERMELHO_FRACO, (20, 20, 204, 22))
    pygame.draw.rect(tela, VERMELHO, (20, 20, jogador.vida * 2.04, 22))
    texto_vida = FONTE_PEQUENA.render(f"VIDA: {int(jogador.vida)}/{jogador.vida_max}", True, BRANCO)
    tela.blit(texto_vida, (25, 21))

    tela.blit(FONTE_MEDIA.render(f"PONTOS: {jogador.pontos}", True, AMARELO), (20, 55))
    tela.blit(FONTE_MEDIA.render(f"ONDA: {onda}", True, BRANCO), (20, 85))

    y = 120
    for nome, dados in jogador.armas.items():
        selado = "◄ SELECIONADO" if jogador.arma_atual == nome else ""
        cor = AMARELO if jogador.arma_atual == nome else BRANCO
        tipo_texto = "BRANCA" if dados['tipo'] == 'branca' else "FOGO"
        tela.blit(FONTE_PEQUENA.render(f"  {nome.upper()} [{tipo_texto}] ∞ {selado}", True, cor), (20, y))
        y += 22

    controles = [
        "WASD / Setas - Mover",
        "Mouse - Mirar",
        "Clique esquerdo - Atacar",
        "1/2/3/4 - Trocar Arma",
        "R - Reiniciar",
        "ESC - Sair"
    ]
    y = ALTURA - len(controles)*22 - 15
    for l in controles:
        tela.blit(FONTE_PEQUENA.render(l, True, (150, 150, 150)), (20, y))
        y += 22

def verificar_ataque_corpo_a_corpo(jogador, inimigos):
    atk = jogador.ataque_ativo
    if not atk or atk["tipo"] != "corpo_a_corpo":
        return []
    atingidos = []
    for inimigo in inimigos:
        dx = inimigo.rect.centerx - jogador.rect.centerx
        dy = inimigo.rect.centery - jogador.rect.centery
        dist = math.hypot(dx, dy)
        angulo_alvo = math.degrees(math.atan2(dy, dx))
        diff = abs(angulo_alvo - atk["angulo"]) % 360
        if dist < atk["alcance"] and (diff < 60 or diff > 300):
            morto = inimigo.tomar_dano(atk["dano"])
            atingidos.append((inimigo, morto))
    return atingidos

def gerar_item_aleatorio(x, y):
    return Item("vida", x, y)

def gerar_inimigos(qtd, jogador, obstaculos, nivel=1):
    novos = []
    tentativas = 0
    while len(novos) < qtd and tentativas < 500:
        tentativas += 1
        x = random.randint(100, MAPA_LARGURA - 100)
        y = random.randint(100, MAPA_ALTURA - 100)
        dist_jogador = math.hypot(x - jogador.rect.centerx, y - jogador.rect.centery)
        if dist_jogador > 350:
            teste = pygame.Rect(x-20, y-20, 40, 40)
            colisao = False
            for obs in obstaculos:
                if teste.colliderect(obs.rect):
                    colisao = True
                    break
            if not colisao:
                novos.append(Inimigo(x, y, nivel))
    return novos

# ===================== JOGO PRINCIPAL =====================

def jogo():
    jogador = Jogador()
    obstaculos = gerar_mapa()
    todos_inimigos = pygame.sprite.Group()
    todos_itens = pygame.sprite.Group()
    todos_projeteis = pygame.sprite.Group()

    superficie_mapa = pygame.Surface((MAPA_LARGURA, MAPA_ALTURA))
    desenhar_fundo_mapa(superficie_mapa)
    obstaculos.draw(superficie_mapa)

    onda = 1
    inimigos_por_onda = 5
    inimigos_restantes = inimigos_por_onda
    estado = "jogando"
    relogio_onda = pygame.time.get_ticks()

    camera = pygame.Rect(
        jogador.rect.centerx - LARGURA//2,
        jogador.rect.centery - ALTURA//2,
        LARGURA, ALTURA
    )
    if camera.left < 0: camera.left = 0
    if camera.right > MAPA_LARGURA: camera.right = MAPA_LARGURA
    if camera.top < 0: camera.top = 0
    if camera.bottom > MAPA_ALTURA: camera.bottom = MAPA_ALTURA

    for inimigo in gerar_inimigos(inimigos_por_onda, jogador, obstaculos, onda):
        todos_inimigos.add(inimigo)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if estado == "fim" and evento.key == pygame.K_r:
                    return jogo()
                if estado == "jogando":
                    if evento.key == pygame.K_1: jogador.trocar_arma("faca")
                    if evento.key == pygame.K_2: jogador.trocar_arma("cacetete")
                    if evento.key == pygame.K_3: jogador.trocar_arma("pistola")
                    if evento.key == pygame.K_4: jogador.trocar_arma("espingarda")
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and estado == "jogando":
                res = jogador.atacar(pygame.mouse.get_pos(), camera)
                if res and res["tipo"] == "tiro":
                    p = Projetil(jogador.rect.centerx, jogador.rect.centery, res["dx"], res["dy"], res["dano"], res["alcance"])
                    todos_projeteis.add(p)

        if estado != "jogando":
            tela.fill(PRETO)
            texto = FONTE_GRANDE.render("GAME OVER", True, VERMELHO)
            tela.blit(texto, (LARGURA//2 - 90, ALTURA//2 - 40))
            tela.blit(FONTE_MEDIA.render(f"Pontuação final: {jogador.pontos}", True, BRANCO), (LARGURA//2 - 110, ALTURA//2 + 5))
            tela.blit(FONTE_PEQUENA.render("Pressione R para reiniciar | ESC para sair", True, BRANCO), (LARGURA//2 - 160, ALTURA//2 + 45))
            pygame.display.flip()
            relogio.tick(FPS)
            continue

        teclas = pygame.key.get_pressed()
        jogador.mover(teclas, [obs.rect for obs in obstaculos])
        jogador.atualizar_angulo(pygame.mouse.get_pos(), camera)
        jogador.update()

        camera = pygame.Rect(
            jogador.rect.centerx - LARGURA//2,
            jogador.rect.centery - ALTURA//2,
            LARGURA, ALTURA
        )
        if camera.left < 0: camera.left = 0
        if camera.right > MAPA_LARGURA: camera.right = MAPA_LARGURA
        if camera.top < 0: camera.top = 0
        if camera.bottom > MAPA_ALTURA: camera.bottom = MAPA_ALTURA

        if inimigos_restantes <= 0 and len(todos_inimigos) == 0:
            if pygame.time.get_ticks() - relogio_onda > 2000:
                onda += 1
                inimigos_por_onda = 5 + onda * 3
                novos = gerar_inimigos(inimigos_por_onda, jogador, obstaculos, onda)
                for inimigo in novos:
                    todos_inimigos.add(inimigo)
                inimigos_restantes = inimigos_por_onda
                relogio_onda = pygame.time.get_ticks()

        for inimigo in list(todos_inimigos):
            inimigo.seguir_jogador(jogador, [obs.rect for obs in obstaculos])

        for inimigo, morto in verificar_ataque_corpo_a_corpo(jogador, todos_inimigos):
            if morto:
                todos_inimigos.remove(inimigo)
                jogador.pontos += inimigo.pontos_valor
                inimigos_restantes -= 1
                if random.random() < 0.3:
                    todos_itens.add(gerar_item_aleatorio(inimigo.rect.centerx, inimigo.rect.centery))

        for proj in list(todos_projeteis):
            status, morto, inimigo = proj.update(todos_inimigos, [obs.rect for obs in obstaculos])
            if status in ["atingiu", "fim", "parede"]:
                todos_projeteis.remove(proj)
                if morto:
                    todos_inimigos.remove(inimigo)
                    jogador.pontos += inimigo.pontos_valor
                    inimigos_restantes -= 1
                    if random.random() < 0.35:
                        todos_itens.add(gerar_item_aleatorio(inimigo.rect.centerx, inimigo.rect.centery))

        for item in list(todos_itens):
            if jogador.rect.colliderect(item.rect):
                item.coletar(jogador)
                todos_itens.remove(item)

        if jogador.vida <= 0:
            estado = "fim"

        desenhar_fundo_mapa(superficie_mapa)
        obstaculos.draw(superficie_mapa)
        todos_itens.draw(superficie_mapa)
        todos_projeteis.draw(superficie_mapa)
        todos_inimigos.draw(superficie_mapa)
        superficie_mapa.blit(jogador.image, jogador.rect)

        tela.blit(superficie_mapa.subsurface(camera), (0, 0))
        desenhar_nevoa()
        desenhar_interface(jogador, onda)
        desenhar_minimapa(jogador, todos_inimigos, obstaculos)

        pygame.display.flip()
        relogio.tick(FPS)

if __name__ == "__main__":
    jogo()