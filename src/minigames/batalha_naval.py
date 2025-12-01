# ===========================================================
#                MINIGAME BATALHA NAVAL (WEB OPTIMIZED)
# ===========================================================

import asyncio
import pygame
import random
import sys
import os
import math
from src.utils import show_pause_screen, draw_score_display, load_font
from src.score_manager import ScoreManager
# CORREÇÃO 1: Importamos a instância minúscula para padronizar
from src.audio_manager import audio_manager 
import src.difficulty_manager as dm

# === SISTEMA DE PARTÍCULAS OTIMIZADO ===
class WaterParticle:
    # __slots__ economiza memória na Web
    __slots__ = ('screen_w', 'screen_h', 'x', 'y', 'radius', 'speed', 'dir_x', 'dir_y', 'osc', 'image', 'rect')

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.reset(first_run=True)
        
        # OTIMIZAÇÃO: Cria a superfície UMA VEZ
        self.radius = random.randint(2, 5)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # Cor fixa da água com alpha base
        pygame.draw.circle(self.image, (160, 200, 255, random.randint(30, 110)), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

    def reset(self, first_run=False):
        self.x = random.uniform(0, self.screen_w)
        self.y = random.uniform(0, self.screen_h)
        self.speed = random.uniform(0.15, 0.7)
        self.dir_x = random.uniform(-0.25, 0.25)
        self.dir_y = random.uniform(-0.05, 0.2)
        self.osc = random.uniform(0, 6.28)

    def update(self):
        self.x += self.dir_x + math.sin(self.osc) * 0.12
        self.y += self.dir_y
        self.osc += 0.04
        
        # Boundary Check
        if self.x < -10: self.x = self.screen_w + 10
        elif self.x > self.screen_w + 10: self.x = -10
        
        if self.y < -10: self.y = self.screen_h + 10
        elif self.y > self.screen_h + 10: self.y = -10

    def draw(self, surface):
        # Blit é muito mais rápido que draw.circle repetido
        surface.blit(self.image, (int(self.x), int(self.y)))

GRID_SIZE = 5
MARGIN = 10

# === BANCO DE AMEAÇAS ===
BANCO_AMEACAS = [
    ("Malware", "Antivírus Corporativo"),
    ("Phishing", "Autenticação Multifator"),
    ("Ransomware", "Backup Offline"),
    ("DDoS", "Firewall de Borda"),
    ("Engenharia Social", "Treinamento"),
    ("Vazamento de Dados", "DLP (Data Loss)"),
    ("Acesso Indevido", "Gestão de Identidade"),
    ("Shadow IT", "Inventário de Ativos"),
    ("Falha Hardware", "Redundância / HA"),
    ("Insider Threat", "Logs de Auditoria"),
    ("SQL Injection", "WAF Seguro"),
    ("Senha Fraca", "Política de Senhas"),
    ("Zero-Day", "Gestão de Patches"),
    ("Man-in-the-Middle", "VPN / Criptografia"),
    ("Dispositivo Perdido", "Disco Criptografado"),
    ("Wi-Fi Inseguro", "WPA3 Enterprise"),
    ("Spyware", "EDR"),
    ("Botnet", "IPS Ativo"),
    ("API Exposta", "API Gateway"),
    ("Bypass Auth", "Pentest Regular")
]

# ===========================================================
#               FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_batalha_naval(screen):
    pygame.display.set_caption("⚓ Batalha Naval - Controles e Ameaças ⚓")
    clock = pygame.time.Clock()

    # === ASSETS ===
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_batalha_naval.png")
    icon_path = os.path.join(assets_dir, "icons", "naval.png")
    
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()
    
    icon_original = None
    if os.path.exists(icon_path):
        icon_original = pygame.image.load(icon_path).convert_alpha()

    layout = {}

    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['bg'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['bg'] = pygame.Surface((w, h))
            layout['bg'].fill((5, 20, 40))
            
        if icon_original:
            size = int(h * 0.08)
            layout['icon'] = pygame.transform.smoothscale(icon_original, (size, size))
        else:
            layout['icon'] = None
            
        layout['CELL_SIZE'] = min(w, h) // (GRID_SIZE + 3)
        total_width = GRID_SIZE * layout['CELL_SIZE'] + (GRID_SIZE - 1) * MARGIN
        total_height = GRID_SIZE * layout['CELL_SIZE'] + (GRID_SIZE - 1) * MARGIN
        layout['offset_x'] = (w - total_width) // 2
        layout['offset_y'] = (h - total_height) // 2 + 40
        layout['total_height'] = total_height
        
        # Cache Fontes
        layout['font_title'] = load_font(max(48, int(h * 0.09)))
        layout['font_text'] = load_font(max(28, int(h * 0.05)))
        layout['font_small'] = load_font(max(20, int(h * 0.04)))
        
        # Cache Título (Evita renderizar todo frame)
        t_txt = "Batalha Naval"
        layout['title_surf'] = layout['font_title'].render(t_txt, True, (255, 255, 255))
        layout['title_shadow'] = layout['font_title'].render(t_txt, True, (0, 0, 0))

    resize_assets(screen)
    
    water_particles = [WaterParticle(screen.get_width(), screen.get_height()) for _ in range(40)]
    splashes = [] 

    # Configuração de Jogo
    qtd_navios_solicitada = dm.get_batalha_naval_threats()
    max_possible = min(GRID_SIZE * GRID_SIZE, len(BANCO_AMEACAS))
    qtd_navios = min(qtd_navios_solicitada, max_possible)
    
    grid = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    indices = random.sample(range(GRID_SIZE * GRID_SIZE), qtd_navios)
    ameacas_escolhidas = random.sample(BANCO_AMEACAS, qtd_navios)
    navios_pos = {idx: ameacas_escolhidas[i] for i, idx in enumerate(indices)}

    reveladas = set()
    efeitos = []
    jogo_ativo = True
    frame = 0
    HOVER_COLOR = (80, 120, 200)

    # ========================= LOOP PRINCIPAL ================================
    while jogo_ativo:
        # Web Performance: Não use dt para lógica simples, use frame ou clock fixo
        frame += 1
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        CELL_SIZE = layout['CELL_SIZE']
        ox = layout['offset_x']
        oy = layout['offset_y']

        # 1. Background
        screen.blit(layout['bg'], (0, 0))

        # 2. Partículas Água
        for p in water_particles:
            p.update()
            p.draw(screen)

        # 3. Título Animado (Com Alpha Otimizado)
        # Em vez de renderizar texto, aplicamos alpha no blit se necessário, ou movemos apenas
        float_y = int(math.sin(frame * 0.05) * 4)
        cx = screen.get_width() // 2
        cy = 60 + float_y
        
        # Sombra
        tr_s = layout['title_shadow'].get_rect(center=(cx + 3, cy + 3))
        screen.blit(layout['title_shadow'], tr_s)
        # Texto
        tr = layout['title_surf'].get_rect(center=(cx, cy))
        screen.blit(layout['title_surf'], tr)

        if layout['icon']:
            screen.blit(layout['icon'], (tr.left - layout['icon'].get_width() - 15, tr.top))
            screen.blit(layout['icon'], (tr.right + 15, tr.top))

        # 4. Tabuleiro
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = ox + col * (CELL_SIZE + MARGIN)
                y = oy + row * (CELL_SIZE + MARGIN)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                is_revelada = (row, col) in reveladas
                is_erro = grid[row][col] == "X"
                
                # Cor Base
                color = (40, 80, 160) # Azul (Água)
                
                if is_revelada:
                    color = (200, 60, 60) # Vermelho (Navio)
                elif is_erro:
                    color = (80, 80, 100) # Cinza (Erro)
                elif rect.collidepoint(mouse_pos) and jogo_ativo:
                    color = HOVER_COLOR

                # Desenho do Quadrado
                # Sombra leve
                pygame.draw.rect(screen, (0, 0, 0, 80), (x+4, y+4, CELL_SIZE, CELL_SIZE), border_radius=6)
                # Corpo
                pygame.draw.rect(screen, color, rect, border_radius=6)
                # Borda
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)

        # 5. Efeitos Visuais (Flash)
        for efeito in efeitos[:]:
            efeito["tempo"] += 1
            progress = efeito["tempo"] / efeito["max_tempo"]
            
            if progress >= 1:
                efeitos.remove(efeito)
                continue
                
            alpha_fx = int(255 * (1 - progress))
            (erow, ecol) = efeito["pos"]
            x = ox + ecol * (CELL_SIZE + MARGIN)
            y = oy + erow * (CELL_SIZE + MARGIN)
            
            cor = (255, 200, 60, alpha_fx) if efeito["tipo"] == "acerto" else (60, 120, 255, alpha_fx)
            
            flash_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            flash_surf.fill(cor)
            screen.blit(flash_surf, (x, y))

        # 6. Splashes (Explosões)
        new_splashes = []
        for s in splashes:
            s["life"] += 1
            if s["life"] >= s["max_life"]: continue
            
            new_splashes.append(s)
            
            # Update física simples
            if "dx" in s: # Partícula
                s["x"] += s["dx"]
                s["y"] += s["dy"]
                s["dy"] += 0.1 # gravidade
                s["alpha"] = max(0, s["alpha"] - 10)
                
                pygame.draw.circle(screen, (200, 230, 255, int(s["alpha"])), (int(s["x"]), int(s["y"])), int(s["r"]))
            else: # Onda de choque
                s["r"] += 1.5
                s["alpha"] = max(0, s["alpha"] - 8)
                pygame.draw.circle(screen, (255, 255, 255, int(s["alpha"])), (int(s["x"]), int(s["y"])), int(s["r"]), 2)
        splashes = new_splashes

        draw_score_display(screen, ScoreManager.get_score(), layout['font_small'], position="topright")

        # Instruções
        # Renderiza uma vez ou usa cache se possível, mas aqui é simples
        # info_s = layout['font_small'].render("Clique para encontrar Riscos", True, (200, 220, 255))
        # screen.blit(info_s, info_s.get_rect(center=(screen.get_width()//2, oy + layout['total_height'] + 30)))

        # === EVENTOS ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    resize_assets(screen)
                elif event.key == pygame.K_ESCAPE:
                    return ScoreManager.get_score()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                
                # Detecta clique no grid
                clicked_cell = None
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        x = ox + col * (CELL_SIZE + MARGIN)
                        y = oy + row * (CELL_SIZE + MARGIN)
                        if pygame.Rect(x, y, CELL_SIZE, CELL_SIZE).collidepoint(mx, my):
                            clicked_cell = (row, col)
                            break
                    if clicked_cell: break
                
                # Lógica do Clique
                if clicked_cell:
                    r, c = clicked_cell
                    if (r, c) not in reveladas and grid[r][c] != "X":
                        cx = ox + c * (CELL_SIZE + MARGIN) + CELL_SIZE//2
                        cy = oy + r * (CELL_SIZE + MARGIN) + CELL_SIZE//2
                        pos_idx = r * GRID_SIZE + c
                        
                        if pos_idx in navios_pos:
                            # --- ACERTO ---
                            reveladas.add((r, c))
                            ameaca, controle = navios_pos[pos_idx]
                            
                            ScoreManager.add_points(10)
                            audio_manager.play_sfx_if_exists("explosion")
                            
                            efeitos.append({"tipo": "acerto", "pos": (r, c), "tempo": 0, "max_tempo": 20})
                            
                            # Cria Splash
                            splashes.append({"x": cx, "y": cy, "r": 5, "alpha": 255, "life": 0, "max_life": 20})
                            for _ in range(8):
                                splashes.append({
                                    "x": cx, "y": cy, "r": random.randint(2,4), "alpha": 255,
                                    "dx": random.uniform(-3, 3), "dy": random.uniform(-4, -1),
                                    "life": 0, "max_life": 25
                                })

                            # --- FIX DELAY ---
                            # Força o desenho da explosão AGORA
                            pygame.display.flip()
                            # Espera um pouco para o usuário ver e ouvir antes do pause
                            await asyncio.sleep(0.15) 
                            
                            await show_pause_screen(screen, clock, "Risco Detectado!", f"Ameaça: {ameaca}", f"Solução: {controle}", theme="Batalha Naval")
                        else:
                            # --- ERRO ---
                            grid[r][c] = "X"
                            ScoreManager.add_points(-5)
                            audio_manager.play_sfx_if_exists("errado")
                            efeitos.append({"tipo": "erro", "pos": (r, c), "tempo": 0, "max_tempo": 20})
                            
                            # Feedback visual rápido
                            pygame.display.flip()
                            await asyncio.sleep(0.1)
                            
                            await show_pause_screen(screen, clock, "Água...", "Nenhum risco aqui.", theme="Batalha Naval")

        # Verifica Vitória
        if len(reveladas) == len(navios_pos):
            # CORREÇÃO 2: Grafia corrigida aqui
            audio_manager.play_sfx_if_exists("correto")
            await show_pause_screen(screen, clock, "Ambiente Seguro!", f"Pontuação Total: {ScoreManager.get_score()}", theme="Batalha Naval")
            jogo_ativo = False

        pygame.display.flip()
        
        # OBRIGATÓRIO NA WEB
        await asyncio.sleep(0)

    return ScoreManager.get_score()