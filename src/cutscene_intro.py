#===============================================
#  CUTSCENE - INTRODUÇÃO DO JOGO (WEB OPTIMIZED)
#===============================================

import pygame
import os
import random
from math import sin
import asyncio  # <--- IMPORTANTE PARA WEB

from src.utils import (
    load_font,
    draw_text,
    draw_text_wrapped,
    draw_modern_container,
    fade_in,
    fade_out
)

from src.audio_manager import audio_manager


# ============================================================
# Pequeno blur eficiente (Memoized)
# ============================================================
def _blur(surface, amount=12):
    """Aplica blur redimensionando (rápido para Web)."""
    if amount <= 1:
        return surface
    w, h = surface.get_size()
    # Reduz drasticamente para perder detalhe
    small = pygame.transform.smoothscale(surface, (max(1, w // amount), max(1, h // amount)))
    # Estica de volta
    return pygame.transform.smoothscale(small, (w, h))


# ============================================================
# Botão PULAR (Skip) - Animado
# ============================================================
class SkipButton:
    def __init__(self, screen_w, font):
        self.text = "PULAR"
        self.font = font
        self.base_color = (200, 50, 50)
        self.hover_color = (230, 80, 80)
        self.text_color = (255, 255, 255)
        
        self.width = 110
        self.height = 45
        self.margin = 25
        
        self.rect = pygame.Rect(
            screen_w - self.width - self.margin,
            self.margin,
            self.width,
            self.height
        )
        
        self.scale = 1.0
        self.target_scale = 1.0
        
        # Otimização: Renderiza texto uma vez
        self.text_surf = self.font.render(self.text, True, self.text_color)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        self.target_scale = 1.1 if is_hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

        anim_w = int(self.width * self.scale)
        anim_h = int(self.height * self.scale)
        
        anim_rect = pygame.Rect(0, 0, anim_w, anim_h)
        anim_rect.center = self.rect.center

        color = self.hover_color if is_hovered else self.base_color

        # Sombra
        shadow_rect = anim_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        pygame.draw.rect(screen, color, anim_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), anim_rect, 2, border_radius=12)
        
        text_rect = self.text_surf.get_rect(center=anim_rect.center)
        screen.blit(self.text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_position(self, screen_w):
        self.rect.topright = (screen_w - self.margin, self.margin)


# ============================================================
# Cutscene Intro (ASYNC / NO LAG)
# ============================================================
async def run_cutscene_intro(screen):
    pygame.display.set_caption("Party Pascal — Introdução")
    clock = pygame.time.Clock()

    # Inicia música imediatamente (Stream)
    audio_manager.fade_to_music("cutscene_intro", fade_ms=800)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")

    bg_path = os.path.join(assets, "background", "curtcene.png")
    pascal_path = os.path.join(assets, "sprites", "pascal.png")

    # ==================================================================
    # PRELOAD ASSETS (Evita travadas no meio da animação)
    # ==================================================================
    W, H = screen.get_size()
    
    # Fontes
    font_title = load_font(int(H * 0.048)) 
    font_body = load_font(int(H * 0.040))
    font_hint = load_font(int(H * 0.028))
    font_particle = load_font(int(H * 0.034))
    font_skip = load_font(int(H * 0.032))

    # Background (Carrega e aplica Blur UMA VEZ)
    if os.path.exists(bg_path):
        try:
            raw = pygame.image.load(bg_path).convert()
            raw = pygame.transform.smoothscale(raw, (W, H))
            bg = _blur(raw, 10)
        except:
            bg = pygame.Surface((W, H)); bg.fill((15, 18, 30))
    else:
        bg = pygame.Surface((W, H)); bg.fill((15, 18, 30))

    # Pascal Sprite
    pascal = None
    if os.path.exists(pascal_path):
        try:
            pascal_orig = pygame.image.load(pascal_path).convert_alpha()
            # Pré-calcula tamanho alvo para evitar redimensionar a cada frame
            target_h = int(H * 0.86)
            ratio = pascal_orig.get_width() / pascal_orig.get_height()
            target_w = int(ratio * target_h)
            pascal = pygame.transform.smoothscale(pascal_orig, (target_w, target_h))
        except:
            pascal = None

    # Cache de partículas (Texto renderizado uma vez)
    particle_chars = ["✦", "✧", "•", "⋆"]
    particle_surfs = [font_particle.render(c, True, (255, 230, 170)) for c in particle_chars]
    
    particles = []
    for i in range(45):
        particles.append({
            "x": random.randint(0, W),
            "y": random.randint(0, H),
            "spd": random.uniform(0.3, 1.0),
            "alpha": random.randint(150, 255),
            "surf": random.choice(particle_surfs) # Usa surface pré-renderizada
        })

    # Glow estático (transparente) para evitar criar surface todo frame
    glow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    
    # ==================================================================
    # SCRIPT
    # ==================================================================
    script = [
        ("Antes da Jornada…",
        "Em um lugar muito além dos servidores e sistemas, existe o Reino da Governança. "
        "Um mundo onde decisões moldam destinos e cada ação pode criar valor… ou caos."),

        ("A Chegada do Guardião",
        "Eu sou Pascal, o seu guia nesta aventura! Fui criado para proteger este reino mantendo ordem, "
        "controle e sabedoria."),

        ("A Ameaça Invisível",
        "Mas algo está errado… riscos ignorados, decisões ruins e operações desorganizadas estão "
        "abalando todo o reino."),

        ("A Essência da Governança",
        "Para restaurar o equilíbrio, você precisará dominar a Governança de TI: "
        "alinhar objetivos, processos, pessoas e tecnologia."),

        ("Os Cinco Guardiões",
        "EDM a direção; APO o planejamento; BAI a construção; DSS a operação; MEA o monitoramento. "
        "Eles são os pilares que sustentam o Reino da Governança."),

        ("Seu Papel",
        "Você enfrentará desafios inspirados em situações reais de Governança, "
        "tomando decisões rápidas, estratégicas e responsáveis."),

        ("Preparado?",
        "O Reino da Governança depende de você. Vamos começar a Festa!")
    ]

    index = 0
    body_text = script[0][1]
    char_index = 0
    char_speed = 18
    last_char = pygame.time.get_ticks()

    pas_x = -500
    pas_alpha = 0
    
    skip_btn = SkipButton(W, font_skip)

    # Fade In suave
    await fade_in(screen)

    running = True
    t = 0

    # ==================================================================
    # LOOP PRINCIPAL
    # ==================================================================
    while running:
        dt = clock.tick(60)
        t += dt
        W, H = screen.get_size()

        # 1. Background (Blit simples é rápido)
        screen.blit(bg, (0, 0))

        # 2. Glow Pulsante Otimizado
        # Em vez de fill a cada frame, ajustamos alpha geral se possível ou limitamos updates
        glow_alpha = int(35 + 20 * sin(t * 0.004))
        glow_surf.fill((60, 90, 180, glow_alpha)) # Ainda necessário, mas surface já existe
        screen.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # 3. Partículas Rápidas (Sem render de texto no loop)
        for p in particles:
            p["y"] -= p["spd"]
            p["alpha"] -= 1

            if p["alpha"] <= 0 or p["y"] < -30:
                p["x"] = random.randint(0, W)
                p["y"] = random.randint(H, H + 150)
                p["alpha"] = random.randint(150, 255)

            # Define alpha na surface cached (copia temp para não afetar outras)
            # Obs: set_alpha em surface com per-pixel alpha às vezes é tricky,
            # mas para partículas simples funciona bem ou ignora-se o alpha fino.
            p["surf"].set_alpha(p["alpha"])
            screen.blit(p["surf"], (p["x"], p["y"]))

        # 4. Pascal Animado
        if pascal:
            # Entrada suave
            target_x = int(W * 0.03)
            pas_x += (target_x - pas_x) * 0.12

            # Respiração leve (rotozoom é pesado, usar com moderação ou pré-cache se travar)
            # Na Web, rotozoom constante pode ser pesado.
            # Se ainda der lag, comente a linha 'rotozoom' abaixo.
            scale = 1.0 + 0.012 * sin(t * 0.005)
            pas_draw = pygame.transform.rotozoom(pascal, 0, scale)

            # Fade do personagem
            pas_alpha = min(255, pas_alpha + 4)
            pas_draw.set_alpha(pas_alpha)

            screen.blit(pas_draw, (pas_x, H - pas_draw.get_height()))

        # 5. UI / Texto
        d_w = int(W * 0.88)
        d_h = int(H * 0.28)
        d_rect = pygame.Rect((W - d_w)//2, int(H * 0.66), d_w, d_h)

        draw_modern_container(screen, d_rect)

        # Título
        draw_text(
            screen,
            script[index][0],
            font_title,
            (255, 230, 170),
            (d_rect.x + 30 + font_title.size(script[index][0])[0]/2, d_rect.y + 25)
        )

        # Máquina de escrever
        now = pygame.time.get_ticks()
        if char_index < len(body_text) and now - last_char >= char_speed:
            char_index += 1
            last_char = now

        ta = d_rect.inflate(-40, -80)
        draw_text_wrapped(
            screen,
            body_text[:char_index],
            font_body,
            (240,240,240),
            ta,
            align="left" 
        )

        # Hint
        if (t // 400) % 2 == 0:
            draw_text(screen, "Clique para avançar", font_hint,
                      (230,230,230), (W//2, int(H * 0.97)))
        
        # Botão Pular
        skip_btn.update_position(W)
        skip_btn.draw(screen)

        # 6. Eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit() # type: ignore

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Clique no SKIP
                if skip_btn.is_clicked(mouse_pos):
                    audio_manager.play_sfx_if_exists("click")
                    await fade_out(screen)
                    return

                # Clique para avançar texto
                audio_manager.play_sfx_if_exists("click")
                if char_index < len(body_text):
                    char_index = len(body_text) # Completa texto instantâneo
                else:
                    index += 1
                    if index >= len(script):
                        await fade_out(screen)
                        return

                    body_text = script[index][1]
                    char_index = 0
                    last_char = pygame.time.get_ticks()

        pygame.display.flip()
        
        # OBRIGATÓRIO: Mantém o browser vivo e responsivo
        await asyncio.sleep(0)