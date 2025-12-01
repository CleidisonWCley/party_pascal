# ===========================================================
#           MINIGAME STOP (WEB OPTIMIZED)
# ===========================================================

import pygame
import sys
import time
import os
import random
import math
import asyncio

from src.utils import show_pause_screen, draw_text_wrapped, draw_question_container, draw_score_display, load_font
from src.score_manager import ScoreManager
# Correção do Import
from src.audio_manager import audio_manager 
import src.difficulty_manager as dm

# ===========================================================
#            BANCO DE PERGUNTAS (MANTIDO)
# ===========================================================
ALL_QUESTIONS = {
    "facil": [
        {"categoria": "Domínio de Governança", "letra": "E", "dica": "Domínio focado em Avaliar, Dirigir e Monitorar.", "opcoes": ["EDM", "Entregar", "Executar", "Estratégia", "Engajar"], "correta": "EDM"},
        {"categoria": "Domínio de Gestão", "letra": "A", "dica": "Domínio focado em Alinhar, Planejar e Organizar.", "opcoes": ["APO", "Avaliar", "Adquirir", "Analisar", "Apoiar"], "correta": "APO"},
        {"categoria": "Domínio de Gestão", "letra": "B", "dica": "Domínio focado em Construir, Adquirir e Implementar.", "opcoes": ["BAI", "Buscar", "Balancear", "Benchmarking", "Basear"], "correta": "BAI"},
        {"categoria": "Domínio de Gestão", "letra": "D", "dica": "Domínio focado em Entregar, Servir e Suportar.", "opcoes": ["DSS", "Desenvolver", "Direcionar", "Diagnosticar", "Documentar"], "correta": "DSS"},
        {"categoria": "Domínio de Gestão", "letra": "M", "dica": "Domínio focado em Monitorar, Avaliar e Analisar.", "opcoes": ["MEA", "Manter", "Melhorar", "Mapear", "Medir"], "correta": "MEA"},
        {"categoria": "Princípio de Governança", "letra": "H", "dica": "Abordagem que considera todos os componentes interconectados.", "opcoes": ["Holística", "Hierárquica", "Humana", "Horizontal", "Homogênea"], "correta": "Holística"}
    ],
    "normal": [
        {"categoria": "Objetivo de Governança", "letra": "V", "dica": "Um dos principais objetivos da governança é a entrega de...", "opcoes": ["Valor", "Vendas", "Velocidade", "Visão", "Validação"], "correta": "Valor"},
        {"categoria": "Componente do Sistema", "letra": "P", "dica": "Componente que descreve as atividades e fluxos de trabalho.", "opcoes": ["Processos", "Pessoas", "Políticas", "Princípios", "Projetos"], "correta": "Processos"},
        {"categoria": "Componente do Sistema", "letra": "E", "dica": "Componente que define a organização e tomada de decisão.", "opcoes": ["Estruturas Organizacionais", "Estratégia", "Ética", "Eficiência", "Escopo"], "correta": "Estruturas Organizacionais"},
        {"categoria": "Fator de Desenho", "letra": "T", "dica": "Fator relacionado ao cenário de ameaças cibernéticas.", "opcoes": ["Threat Landscape", "Tecnologia", "Tempo", "Tamanho", "Transparência"], "correta": "Threat Landscape"},
        {"categoria": "Área de Foco", "letra": "S", "dica": "Área crítica que lida com proteção de dados e ativos.", "opcoes": ["Segurança Cibernética", "Serviços", "Sistemas", "Suporte", "Software"], "correta": "Segurança Cibernética"},
        {"categoria": "Papel de Gestão", "letra": "C", "dica": "Executivo responsável pela tecnologia (sigla).", "opcoes": ["CIO", "CEO", "CFO", "COO", "CTO"], "correta": "CIO"}
    ],
    "dificil": [
        {"categoria": "Conceito Avançado", "letra": "G", "dica": "Diferença fundamental entre Governança e...", "opcoes": ["Gestão", "Gasto", "Ganho", "Garantia", "Guia"], "correta": "Gestão"},
        {"categoria": "Objetivo de Gestão", "letra": "R", "dica": "APO12 foca na gestão de...", "opcoes": ["Risco", "Recursos", "Requisitos", "Relatórios", "Redes"], "correta": "Risco"},
        {"categoria": "Objetivo de Gestão", "letra": "Q", "dica": "APO11 foca na gestão da...", "opcoes": ["Qualidade", "Quantidade", "Questão", "Quadro", "Quota"], "correta": "Qualidade"},
        {"categoria": "Padrão Relacionado", "letra": "I", "dica": "Padrão para gestão de serviços de TI.", "opcoes": ["ITIL", "ISO", "IEEE", "ISACA", "IAM"], "correta": "ITIL"},
        {"categoria": "Padrão Relacionado", "letra": "P", "dica": "Guia de boas práticas para gestão de projetos.", "opcoes": ["PMBOK", "Prince2", "PDCA", "Padrão", "Plano"], "correta": "PMBOK"},
        {"categoria": "Conceito de Design", "letra": "D", "dica": "Sistema de governança que se adapta a mudanças.", "opcoes": ["Dinâmico", "Direto", "Digital", "Durável", "Definido"], "correta": "Dinâmico"}
    ]
}

# ===========================================================
#        PARTÍCULAS OTIMIZADAS (CACHE)
# ===========================================================
class StopParticle:
    __slots__ = ('x', 'y', 'speed', 'base_alpha', 'scale', 'rotation', 'rot_speed', 'image', 'rect', 'w', 'h')
    
    # Cache estático de surfaces para não recriar a cada partícula
    _cached_surfaces = []

    @classmethod
    def pre_render_surfaces(cls, font):
        cls._cached_surfaces = []
        chars = ["S", "T", "O", "P", "?", "!", "$"]
        colors = [
            (255, 80, 80), (80, 255, 255), (255, 255, 80), (180, 80, 255)
        ]
        for char in chars:
            for col in colors:
                surf = font.render(char, True, col)
                cls._cached_surfaces.append(surf)

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset(first_time=True)

    def reset(self, first_time=False):
        self.x = random.randint(20, self.w - 20)
        if first_time:
            self.y = random.randint(0, self.h)
        else:
            self.y = random.randint(self.h, self.h + 100)
            
        self.speed = random.uniform(0.5, 2.0)
        self.base_alpha = random.randint(40, 100)
        self.scale = random.uniform(0.6, 1.4)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)
        
        # Pega uma surface já pronta
        if not StopParticle._cached_surfaces: return
        base = random.choice(StopParticle._cached_surfaces)
        
        # Escala apenas na criação (não no draw)
        nw = int(base.get_width() * self.scale)
        nh = int(base.get_height() * self.scale)
        if nw > 0 and nh > 0:
            self.image = pygame.transform.smoothscale(base, (nw, nh))
        else:
            self.image = base
        
        self.image.set_alpha(self.base_alpha)
        self.rect = self.image.get_rect()

    def update(self, dt):
        self.y -= self.speed * dt
        self.rotation += self.rot_speed * dt
        if self.y < -50:
            self.reset()

    def draw(self, screen):
        # Rotação em tempo real ainda é necessária, mas surface base é leve
        # Para otimização máxima, poderíamos evitar rotate a cada frame se travar
        rot_img = pygame.transform.rotate(self.image, self.rotation)
        screen.blit(rot_img, (int(self.x) - rot_img.get_width()//2, int(self.y) - rot_img.get_height()//2))


# ===========================================================
#        ANIMAÇÃO DE ROLETA (ASYNC)
# ===========================================================
async def animar_roleta(screen, letra_alvo, layout, clock):
    letras_random = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    w, h = screen.get_size()
    
    velocidade = 50 
    total_giros = 20
    
    # Pre-render grid (uma vez)
    grid_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(0, w, 40):
        pygame.draw.line(grid_surf, (255, 255, 255, 10), (x, 0), (x, h))
    
    txt_sorteio = layout['font_text'].render("Sorteando Letra...", True, (200, 200, 200))
    txt_rect = txt_sorteio.get_rect(center=(w//2, h*0.3))

    for i in range(total_giros):
        screen.fill((15, 15, 30))
        screen.blit(grid_surf, (0,0))
        screen.blit(txt_sorteio, txt_rect)
        
        if i < total_giros - 1:
            char_atual = random.choice(letras_random)
            cor = (150, 150, 150)
            scale = 1.0
        else:
            char_atual = letra_alvo
            cor = (255, 215, 0)
            scale = 1.5

        # Usa cache de letras grandes se possível, ou renderiza aqui (poucas vezes)
        letra_surf = layout['font_letra'].render(char_atual, True, cor)
        
        if scale != 1.0:
            nw = int(letra_surf.get_width() * scale)
            nh = int(letra_surf.get_height() * scale)
            letra_surf = pygame.transform.scale(letra_surf, (nw, nh))

        rect = letra_surf.get_rect(center=(w//2, h//2))
        screen.blit(letra_surf, rect)
        
        pygame.display.flip()
        
        if i > total_giros - 8:
            velocidade += 40 
        
        await asyncio.sleep(velocidade / 1000.0)

    # Flash
    flash = pygame.Surface((w, h))
    flash.fill((255, 255, 255))
    screen.blit(flash, (0,0))
    pygame.display.flip()
    
    await asyncio.sleep(0.05)
    audio_manager.play_sfx_if_exists("explosion")


# ===========================================================
#             FUNÇÃO PRINCIPAL (ASYNC)
# ===========================================================
async def run_stop(screen):
    pygame.display.set_caption("STOP - Governança de TI")
    clock = pygame.time.Clock()

    layout = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets_dir = os.path.join(base_dir, "assets")
    bg_path = os.path.join(assets_dir, "background", "background_stop.png")
    
    bg_original = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else None

    # === RESIZE & CACHE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
        else:
            layout['background'] = pygame.Surface((w, h)); layout['background'].fill((15, 15, 35))

        layout['font_title'] = load_font(max(32, int(h * 0.07)))
        layout['font_text'] = load_font(max(24, int(h * 0.05)))
        layout['font_small'] = load_font(max(20, int(h * 0.04)))
        layout['font_letra'] = load_font(max(180, int(h * 0.35))) 
        layout['font_particle'] = load_font(max(40, int(h * 0.08)))
        
        # Pre-render particles
        StopParticle.pre_render_surfaces(layout['font_particle'])
        
        # Cache Titulo
        layout['title_surf'] = layout['font_title'].render("STOP - Governança de TI", True, (255, 215, 0))
        layout['title_rect'] = layout['title_surf'].get_rect(center=(w // 2, int(h * 0.07)))

    resize_assets(screen)

    particles = [StopParticle(screen.get_width(), screen.get_height()) for _ in range(25)]

    diff_rules = dm.get_rules()
    q_type = dm.get_question_set_type()
    
    perguntas = ALL_QUESTIONS.get(q_type, ALL_QUESTIONS["normal"])
    random.shuffle(perguntas)
    
    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]
    pontos_desta_fase = 0
    shake_amount = 0

    # === CACHE DE UI ATUAL ===
    current_ui_surf = None
    current_buttons = [] # Lista de (rect, texto, surface_texto)

    def cache_ui(pergunta):
        nonlocal current_ui_surf, current_buttons
        w, h = screen.get_size()
        
        # 1. Container Flutuante
        cont_w = int(w * 0.8)
        cont_h = int(h * 0.24)
        s = pygame.Surface((cont_w, cont_h), pygame.SRCALPHA)
        
        # Fundo
        pygame.draw.rect(s, (20, 30, 60, 180), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, (80, 220, 255), s.get_rect(), 2, border_radius=15)
        
        # Letra
        cx, cy = 55, 45 # relativo
        letra_surf = layout['font_title'].render(pergunta['letra'], True, (255, 215, 0))
        pygame.draw.circle(s, (255, 215, 0), (cx, cy), 40, 3)
        s.blit(letra_surf, letra_surf.get_rect(center=(cx, cy)))
        
        # Textos
        cat_surf = layout['font_text'].render(f"Categoria: {pergunta['categoria']}", True, (230, 230, 255))
        s.blit(cat_surf, (cx + 60, cy - 20))
        
        dica_rect = pygame.Rect(cx + 60, cy + 20, cont_w - 140, cont_h - 70)
        draw_text_wrapped(s, f"Dica: {pergunta['dica']}", layout['font_small'], (180, 200, 220), dica_rect, align="left")
        
        current_ui_surf = s
        
        # 2. Botões
        current_buttons = []
        opcoes = pergunta['opcoes']
        
        btn_w = int(min(w * 0.25, 340))
        btn_h = int(min(h * 0.12, 110))
        spacing = int(min(w * 0.04, 30))
        
        # A posição Y será calculada no loop para flutuar junto, aqui definimos a grid
        num_colunas = 3
        grid_w = num_colunas * btn_w + (num_colunas - 1) * spacing
        start_x = (w - grid_w) // 2
        
        for i, txt in enumerate(opcoes):
            linha = i // num_colunas
            coluna = i % num_colunas
            
            # Cache do texto
            txt_surf = layout['font_small'].render(txt, True, (255, 255, 255))
            if txt_surf.get_width() > btn_w - 20:
                sc = (btn_w - 20) / txt_surf.get_width()
                txt_surf = pygame.transform.smoothscale(txt_surf, (int(txt_surf.get_width()*sc), int(txt_surf.get_height()*sc)))
            
            # Offset relativo na grid
            rel_x = start_x + coluna * (btn_w + spacing)
            rel_y_offset = linha * (btn_h + spacing)
            
            current_buttons.append({
                "text": txt,
                "surf": txt_surf,
                "rel_x": rel_x,
                "rel_y_offset": rel_y_offset,
                "w": btn_w, "h": btn_h,
                "rect": pygame.Rect(0,0,0,0) # Será atualizado no loop
            })

    # === LOOP DE PERGUNTAS ===
    for pergunta in perguntas:
        random.shuffle(pergunta["opcoes"])
        
        await animar_roleta(screen, pergunta["letra"], layout, clock)
        
        cache_ui(pergunta)
        
        rodada_ativa = True
        start_time = time.time()
        feedback_color = None
        selected_btn_idx = -1

        while rodada_ativa:
            dt = clock.tick(60) / 16.0
            w, h = screen.get_size()
            
            if shake_amount > 0:
                shake_amount -= 0.5
                if shake_amount < 0: shake_amount = 0
            shake_x = random.randint(-int(shake_amount), int(shake_amount))
            shake_y = random.randint(-int(shake_amount), int(shake_amount))

            screen.blit(layout['background'], (0, 0))
            for p in particles:
                p.update(dt)
                p.draw(screen)

            # Overlay
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 140))
            screen.blit(overlay, (0, 0))
            
            # Título
            t_rect = layout['title_rect'].move(shake_x, shake_y)
            screen.blit(layout['title_surf'], t_rect)
            draw_score_display(screen, ScoreManager.get_score(), layout['font_text'], position="topright")

            # UI Flutuante
            float_val = math.sin(pygame.time.get_ticks() * 0.003) * 6
            cont_y = int(h * 0.16) + float_val + shake_y
            cont_x = int(w * 0.1) + shake_x
            screen.blit(current_ui_surf, (cont_x, cont_y))
            
            # Botões
            mouse_pos = pygame.mouse.get_pos()
            base_btn_y = int(h * 0.50) + float_val + shake_y
            
            for i, btn in enumerate(current_buttons):
                rx = btn["rel_x"] + shake_x
                ry = base_btn_y + btn["rel_y_offset"]
                r = pygame.Rect(rx, ry, btn["w"], btn["h"])
                btn["rect"] = r # Atualiza para clique
                
                is_hover = r.collidepoint(mouse_pos)
                
                # Cores
                if feedback_color and selected_btn_idx == i:
                    bg = feedback_color
                    border = (255, 255, 255)
                elif is_hover:
                    bg = (100, 120, 220, 200)
                    border = (255, 255, 255)
                else:
                    bg = (40, 50, 90, 160)
                    border = (100, 150, 200)
                
                # Desenha direto na tela (rápido)
                pygame.draw.rect(screen, (0,0,0,100), r.move(4,6), border_radius=12)
                pygame.draw.rect(screen, bg, r, border_radius=12)
                pygame.draw.rect(screen, border, r, 2 if not is_hover else 3, border_radius=12)
                
                # Texto cacheado
                ts = btn["surf"]
                screen.blit(ts, ts.get_rect(center=r.center))

            if feedback_color:
                flash = pygame.Surface((w, h), pygame.SRCALPHA)
                flash.fill(feedback_color + (50,))
                screen.blit(flash, (0,0))

            pygame.display.flip()
            await asyncio.sleep(0)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    screen = pygame.display.get_surface()
                    resize_assets(screen)
                    particles = [StopParticle(screen.get_width(), screen.get_height()) for _ in range(25)]
                    cache_ui(pergunta)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return pontos_desta_fase

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and selected_btn_idx == -1:
                    for i, btn in enumerate(current_buttons):
                        if btn["rect"].collidepoint(event.pos):
                            selected_btn_idx = i
                            tempo_total = round(time.time() - start_time, 2)
                            
                            is_correct = (btn["text"] == pergunta["correta"])
                            
                            if is_correct:
                                pontos_desta_fase += pontos_acerto
                                ScoreManager.add_points(pontos_acerto)
                                feedback_msg = "Correto!"
                                feedback_color = (50, 255, 50)
                                audio_manager.play_sfx_if_exists("correto")
                            else:
                                pontos_desta_fase += pontos_erro
                                ScoreManager.add_points(pontos_erro)
                                feedback_msg = "Incorreto!"
                                feedback_color = (255, 50, 50)
                                audio_manager.play_sfx_if_exists("errado")
                                shake_amount = 15
                            
                            # Renderiza feedback visual (1 frame)
                            pygame.display.flip()
                            await asyncio.sleep(0.5)
                            
                            await show_pause_screen(
                                screen, clock,
                                feedback_msg,
                                f"Pontos: {ScoreManager.get_score()} | Tempo: {tempo_total}s",
                                f"Categoria: {pergunta['categoria']}",
                                theme="STOP"
                            )
                            rodada_ativa = False
                            break

    # Final
    audio_manager.play_sfx_if_exists("roleta")
    await show_pause_screen(screen, clock, "Fim do Desafio STOP!", f"Pontuação Final: {ScoreManager.get_score()}", theme="STOP")
    return pontos_desta_fase