# ===========================================================
#           MINIGAME SHOW DO BILHÃO (WEB OPTIMIZED)
# ===========================================================

import asyncio
import pygame
import sys
import os
import random
import math
import time

# Imports do projeto
from src.utils import draw_text_wrapped, draw_score_display, load_font, show_pause_screen
from src.score_manager import ScoreManager
from src.audio_manager import audio_manager
import src.difficulty_manager as dm

# ===========================================================
#            BANCO DE PERGUNTAS (MANTIDO)
# ===========================================================
ALL_QUESTIONS = {
    "facil": [
        {
            "pergunta": "Qual é o principal objetivo da Governança de TI?",
            "opcoes": {"A": "Consertar computadores", "B": "Alinhar TI aos objetivos estratégicos", "C": "Criar jogos digitais", "D": "Instalar redes Wi-Fi"},
            "resposta": "B",
            "motivos": {"B": "A Governança garante que a tecnologia suporte e estenda as estratégias e objetivos da organização."}
        },
        {
            "pergunta": "O COBIT faz uma distinção clara entre dois conceitos. Quais são?",
            "opcoes": {"A": "Hardware e Software", "B": "Governança e Gestão", "C": "Lucro e Prejuízo", "D": "Diretores e Gerentes"},
            "resposta": "B",
            "motivos": {"B": "O COBIT separa claramente as atividades de Governança (avaliar/dirigir) das de Gestão (planejar/executar)."}
        },
        {
            "pergunta": "Quem é o principal responsável pela Governança Corporativa?",
            "opcoes": {"A": "O suporte técnico", "B": "O Conselho de Administração (Board)", "C": "O estagiário de TI", "D": "O fornecedor de internet"},
            "resposta": "B",
            "motivos": {"B": "A Governança é responsabilidade da alta direção/conselho, definindo a direção e monitorando resultados."}
        },
        {
            "pergunta": "O que significa a sigla 'I&T' no contexto do COBIT?",
            "opcoes": {"A": "Internet e Telefonia", "B": "Informação e Tecnologia", "C": "Instalação e Testes", "D": "Inovação e Trabalho"},
            "resposta": "B",
            "motivos": {"B": "O COBIT foca na governança e gestão de Informação e Tecnologia (I&T) em toda a empresa."}
        },
        {
            "pergunta": "Qual domínio cuida da 'Entrega e Suporte' dos serviços?",
            "opcoes": {"A": "EDM", "B": "BAI", "C": "DSS", "D": "APO"},
            "resposta": "C",
            "motivos": {"C": "DSS (Deliver, Service and Support) foca na entrega, serviço e suporte operacional de TI."}
        },
        {
            "pergunta": "O COBIT é um framework desenvolvido por qual organização?",
            "opcoes": {"A": "NASA", "B": "FIFA", "C": "ISACA", "D": "Google"},
            "resposta": "C",
            "motivos": {"C": "O COBIT é desenvolvido pela ISACA para apoiar a governança e gestão de TI."}
        }
    ],
    "normal": [
        {
            "pergunta": "Qual é o único domínio do COBIT focado exclusivamente em GOVERNANÇA?",
            "opcoes": {"A": "EDM (Evaluate, Direct, Monitor)", "B": "APO (Align, Plan, Organize)", "C": "BAI (Build, Acquire, Implement)", "D": "MEA (Monitor, Evaluate, Assess)"},
            "resposta": "A",
            "motivos": {"A": "EDM (Avaliar, Dirigir, Monitorar) é o domínio de Governança. Os outros 4 são de Gestão."}
        },
        {
            "pergunta": "Qual domínio trata da aquisição e implementação de soluções (projetos)?",
            "opcoes": {"A": "EDM", "B": "APO", "C": "BAI", "D": "DSS"},
            "resposta": "C",
            "motivos": {"C": "BAI (Build, Acquire, Implement) gerencia a definição, aquisição e implementação de soluções de TI."}
        },
        {
            "pergunta": "O princípio 'Holistic Approach' (Abordagem Holística) significa que:",
            "opcoes": {"A": "Foca apenas no software", "B": "Considera processos, pessoas e tecnologia", "C": "Ignora a cultura da empresa", "D": "Foca apenas no lucro"},
            "resposta": "B",
            "motivos": {"B": "Uma abordagem holística considera todos os componentes (processos, estruturas, cultura, info) interconectados."}
        },
        {
            "pergunta": "O domínio MEA (Monitor, Evaluate, Assess) é responsável por:",
            "opcoes": {"A": "Escrever códigos", "B": "Avaliação de desempenho e conformidade", "C": "Contratar funcionários", "D": "Comprar servidores"},
            "resposta": "B",
            "motivos": {"B": "MEA foca no monitoramento, avaliação e análise de conformidade e performance."}
        },
        {
            "pergunta": "Na distinção do COBIT, qual é o papel da GESTÃO?",
            "opcoes": {"A": "Avaliar e Dirigir", "B": "Planejar, Construir, Executar e Monitorar", "C": "Apenas Monitorar", "D": "Ignorar a estratégia"},
            "resposta": "B",
            "motivos": {"B": "A Gestão planeja, constrói, executa e monitora atividades alinhadas à direção da Governança."}
        },
        {
            "pergunta": "Qual princípio garante que o sistema de governança atenda às necessidades específicas?",
            "opcoes": {"A": "End-to-End System", "B": "Tailored to Enterprise Needs", "C": "Dynamic System", "D": "Open and Flexible"},
            "resposta": "B",
            "motivos": {"B": "'Tailored to Enterprise Needs' significa adaptar o sistema às necessidades específicas da empresa."}
        }
    ],
    "dificil": [
        {
            "pergunta": "Para 'Gestão de Serviços de TI', o COBIT se integra melhor com:",
            "opcoes": {"A": "PMBOK", "B": "ITIL", "C": "ISO 27001", "D": "Scrum"},
            "resposta": "B",
            "motivos": {"B": "ITIL é o padrão de mercado para Gestão de Serviços e se integra ao domínio DSS do COBIT."}
        },
        {
            "pergunta": "Para 'Segurança da Informação', qual padrão complementa o COBIT?",
            "opcoes": {"A": "ISO 9001", "B": "ISO 27001", "C": "PMBOK", "D": "Six Sigma"},
            "resposta": "B",
            "motivos": {"B": "A ISO 27001 é o padrão global para Segurança da Informação citado na integração com COBIT."}
        },
        {
            "pergunta": "O PMBOK se integra ao COBIT principalmente para apoiar:",
            "opcoes": {"A": "Operação de Service Desk", "B": "Gestão de Projetos", "C": "Auditoria Contábil", "D": "Segurança Física"},
            "resposta": "B",
            "motivos": {"B": "PMBOK fornece as melhores práticas para Gestão de Projetos dentro da governança."}
        },
        {
            "pergunta": "O uso de Modelos de Maturidade no COBIT serve para:",
            "opcoes": {"A": "Aumentar o salário", "B": "Análise de 'gap' (estado atual vs. desejado)", "C": "Eliminar a gerência", "D": "Criar logotipos"},
            "resposta": "B",
            "motivos": {"B": "A maturidade permite medir o desempenho atual e identificar o 'gap' para atingir o nível desejado."}
        },
        {
            "pergunta": "O domínio APO (Align, Plan, Organize) lida com:",
            "opcoes": {"A": "Organização, estratégia e portfólio", "B": "Suporte ao usuário final", "C": "Monitoramento de compliance", "D": "Codificação de software"},
            "resposta": "A",
            "motivos": {"A": "APO foca no alinhamento, planejamento e organização da estratégia e portfólio de TI."}
        },
        {
            "pergunta": "Um Sistema de Governança Dinâmico (Dynamic Governance System) significa:",
            "opcoes": {"A": "Mudar de regras todo dia", "B": "Adaptar-se a mudanças na estratégia/tecnologia", "C": "Não ter regras fixas", "D": "Usar apenas tecnologia nuvem"},
            "resposta": "B",
            "motivos": {"B": "Ser dinâmico significa que o sistema de governança evolui conforme as mudanças de estratégia e tecnologia."}
        }
    ]
}

# ===========================================================
#        SISTEMA DE PARTÍCULAS OTIMIZADO (CACHE)
# ===========================================================
class MoneyParticle:
    """Partículas financeiras que flutuam no fundo"""
    __slots__ = ('x', 'y', 'speed', 'rotation', 'rot_speed', 'image', 'rect', 'w', 'h')

    def __init__(self, w, h, font):
        self.w, self.h = w, h
        # OTIMIZAÇÃO: Cria a surface UMA VEZ
        color = random.choice([
            (255, 215, 0), (0, 255, 0), (0, 255, 255), (180, 180, 180)
        ])
        base_surf = font.render("$", True, color)
        
        # Escala aleatória fixa na criação
        scale = random.uniform(0.5, 1.2)
        nw = int(base_surf.get_width() * scale)
        nh = int(base_surf.get_height() * scale)
        if nw > 0 and nh > 0:
            self.image = pygame.transform.smoothscale(base_surf, (nw, nh))
        else:
            self.image = base_surf
            
        # Define alpha base
        self.image.set_alpha(random.randint(50, 150))
        
        self.reset(first_time=True)

    def reset(self, first_time=False):
        self.x = random.randint(20, self.w - 20)
        if first_time:
            self.y = random.randint(0, self.h)
        else:
            self.y = random.randint(self.h, self.h + 100)
        
        self.speed = random.uniform(0.5, 2.5)
        # Removida rotação contínua (pesada na web) para apenas visual estático ou leve
        # Para performance máxima, não rotacionamos a cada frame.
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -50:
            self.reset()
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ExplosionParticle:
    """Partículas simples de explosão"""
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'decay', 'image')
    
    def __init__(self, x, y, font):
        self.x, self.y = x, y
        
        # Física
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 9)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = 255
        self.decay = random.uniform(8, 15) # Decaimento mais rápido para limpar memória
        
        # Renderiza uma vez
        color = random.choice([(255, 215, 0), (50, 255, 50), (255, 255, 200)])
        base = font.render("$", True, color)
        size = random.uniform(0.4, 0.7)
        w = int(base.get_width() * size)
        h = int(base.get_height() * size)
        if w > 0 and h > 0:
            self.image = pygame.transform.scale(base, (w, h))
        else:
            self.image = base

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2 # gravidade
        self.life -= self.decay

    def draw(self, screen):
        if self.life > 0:
            self.image.set_alpha(int(max(0, self.life)))
            screen.blit(self.image, (int(self.x), int(self.y)))


# ===========================================================
#         UI OPTIMIZED - CACHE DE COMPONENTES
# ===========================================================

class CyberButton:
    """Botão que renderiza seu estado normal e hover APENAS na criação"""
    def __init__(self, rect, text, font):
        self.rect = rect
        self.text = text
        self.is_hover = False
        
        # 1. Pré-renderiza estado NORMAL
        self.surf_normal = self._create_surface((30, 30, 60, 180), (100, 100, 140), (200, 200, 220), font, False)
        
        # 2. Pré-renderiza estado HOVER
        self.surf_hover = self._create_surface((255, 215, 0, 80), (255, 255, 100), (255, 255, 255), font, True)
        
        # 3. Pré-renderiza estados de FEEDBACK (Verde/Vermelho) - Opcional, criado sob demanda ou aqui
        self.surf_correct = self._create_surface((0, 180, 0, 180), (255, 255, 255), (255, 255, 255), font, False)
        self.surf_wrong = self._create_surface((180, 0, 0, 180), (255, 255, 255), (255, 255, 255), font, False)

    def _create_surface(self, bg_color, border_color, text_color, font, is_hover):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Fundo
        pygame.draw.rect(s, bg_color, s.get_rect(), border_radius=10)
        # Borda
        pygame.draw.rect(s, border_color, s.get_rect(), 2 if not is_hover else 3, border_radius=10)
        
        # Decor
        hex_color = (255, 215, 0) if is_hover else (80, 80, 100)
        pygame.draw.circle(s, hex_color, (25, self.rect.height//2), 6)
        
        # Texto
        txt = font.render(self.text, True, text_color)
        # Ajuste de tamanho se for muito grande
        max_w = self.rect.width - 60
        if txt.get_width() > max_w:
            scale = max_w / txt.get_width()
            txt = pygame.transform.smoothscale(txt, (int(txt.get_width()*scale), int(txt.get_height()*scale)))
        
        text_rect = txt.get_rect(midleft=(50, self.rect.height//2))
        s.blit(txt, text_rect)
        return s

    def draw(self, screen, feedback_state=None):
        # 0 = Normal, 1 = Correto, 2 = Errado
        if feedback_state == 1:
            screen.blit(self.surf_correct, self.rect)
        elif feedback_state == 2:
            screen.blit(self.surf_wrong, self.rect)
        elif self.is_hover:
            screen.blit(self.surf_hover, self.rect)
        else:
            screen.blit(self.surf_normal, self.rect)
            
    def check_hover(self, pos):
        self.is_hover = self.rect.collidepoint(pos)


def create_cached_container(rect, question_idx, total, text, font_q):
    """Gera uma Surface transparente contendo a caixa e o texto da pergunta já quebrado"""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # 1. Fundo Glass
    glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    glass.fill((10, 15, 30, 200))
    s.blit(glass, (0,0))
    
    # 2. Borda e Tech
    pygame.draw.rect(s, (180, 160, 50), s.get_rect(), 1, border_radius=2)
    corner = 20
    color = (255, 215, 0)
    # Desenha cantos (simplificado)
    r = s.get_rect()
    pygame.draw.lines(s, color, False, [(r.left, r.top+corner), (r.left, r.top), (r.left+corner, r.top)], 3)
    pygame.draw.lines(s, color, False, [(r.right-corner, r.top), (r.right, r.top), (r.right, r.top+corner)], 3)
    pygame.draw.lines(s, color, False, [(r.left, r.bottom-corner), (r.left, r.bottom), (r.left+corner, r.bottom)], 3)
    pygame.draw.lines(s, color, False, [(r.right-corner, r.bottom), (r.right, r.bottom), (r.right, r.bottom-corner)], 3)

    # 3. Header
    header_rect = pygame.Rect(0, -30, 160, 30)
    # Nota: Desenhar fora da surface cortaria. Vamos desenhar o header dentro do loop principal ou ajustar a surface.
    # Para simplificar, desenhamos o texto da pergunta:
    
    padding = 30
    text_area = r.inflate(-padding*2, -padding*1.5)
    text_area.y += 10
    
    # Usa a função draw_text_wrapped mas desenha NA SURFACE 's'
    # Precisamos importar ou reimplementar draw_text_wrapped para aceitar 's' localmente
    # Como draw_text_wrapped do utils desenha na screen global ou surface passada, passamos 's'
    # e ajustamos o rect para ser relativo a (0,0)
    local_text_area = pygame.Rect(padding, padding + 10, text_area.width, text_area.height)
    draw_text_wrapped(s, text, font_q, (255, 255, 255), local_text_area)
    
    return s

# ===========================================================
#               FUNÇÃO PRINCIPAL DO MINIGAME (ASYNC)
# ===========================================================
async def run_show_do_bilhao(screen):
    pygame.display.set_caption("Show do Bilhão - Cyber Edition")
    clock = pygame.time.Clock()

    layout = {}
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assets = os.path.join(base, "assets")
    bg_path = os.path.join(assets, "background", "background_show_do_bilhao.jpg") 
    icon_path = os.path.join(assets, "icons", "money.png")
    
    # Carrega imagens brutas
    bg_original = None
    if os.path.exists(bg_path):
        bg_original = pygame.image.load(bg_path).convert()
    
    icon_original = None
    if os.path.exists(icon_path):
        icon_original = pygame.image.load(icon_path).convert_alpha()

    # === RESIZE & CACHE ===
    def resize_assets(surface):
        w, h = surface.get_size()
        
        # Background Cache
        if bg_original:
            layout['background'] = pygame.transform.scale(bg_original, (w, h))
            dark = pygame.Surface((w, h))
            dark.fill((0, 0, 0))
            dark.set_alpha(100)
            layout['background'].blit(dark, (0,0))
        else:
            layout['background'] = pygame.Surface((w, h))
            layout['background'].fill((10, 10, 20))

        # Fontes
        layout['font_titulo'] = load_font(int(h * 0.09))
        layout['font_pergunta'] = load_font(int(h * 0.045))
        layout['font_opcao'] = load_font(int(h * 0.035))
        layout['font_particle'] = load_font(int(h * 0.06))
        layout['font_ui'] = load_font(int(h * 0.03))
        
        # Header Estático (Título) - Renderiza UMA vez
        title_txt = "SHOW DO BILHÃO"
        t_surf = layout['font_titulo'].render(title_txt, True, (255, 255, 255))
        layout['title_surf'] = t_surf
        layout['title_rect'] = t_surf.get_rect(center=(w // 2, int(h * 0.08)))
        
        # Ícone
        if icon_original:
            icon_size = int(h * 0.12)
            layout['icon'] = pygame.transform.smoothscale(icon_original, (icon_size, icon_size))
        else:
            layout['icon'] = None

    resize_assets(screen)
    
    bg_particles = [MoneyParticle(screen.get_width(), screen.get_height(), layout['font_particle']) for _ in range(25)]
    explosion_particles = []

    # Configuração de Jogo
    diff_rules = dm.get_rules()
    questions_type = dm.get_question_set_type() 
    raw_questions = ALL_QUESTIONS.get(questions_type, ALL_QUESTIONS["normal"])
    
    perguntas = []
    for q in raw_questions:
        opcoes_texto = list(q["opcoes"].values())
        random.shuffle(opcoes_texto)
        perguntas.append({
            "pergunta": q["pergunta"],
            "opcoes_embaralhadas": opcoes_texto,
            "texto_correto": q["opcoes"][q["resposta"]],
            "motivo_correto": q["motivos"][q["resposta"]]
        })
    random.shuffle(perguntas)

    pontos_acerto = 10 + diff_rules["bonus_acerto"]
    pontos_erro = -diff_rules["perda_pontos"]
    
    pergunta_idx = 0
    feedback = None
    FEEDBACK_DURATION = 2500
    shake_amount = 0

    # Estado da Interface (Cache da pergunta atual)
    current_container_surf = None
    current_container_rect = None
    current_buttons = []

    def setup_question_ui(idx):
        nonlocal current_container_surf, current_container_rect, current_buttons
        w, h = screen.get_size()
        p = perguntas[idx]
        
        # 1. Container da Pergunta
        c_width = w * 0.85
        c_height = h * 0.22
        c_x = (w - c_width) // 2
        c_y = (layout['title_rect'].bottom + 60)
        current_container_rect = pygame.Rect(c_x, c_y, c_width, c_height)
        
        current_container_surf = create_cached_container(
            current_container_rect, idx + 1, len(perguntas), 
            p["pergunta"], layout['font_pergunta']
        )
        
        # 2. Botões
        current_buttons = []
        btn_start_y = current_container_rect.bottom + 30
        btn_h = min(80, int(h * 0.10))
        btn_spacing = 15
        btn_w = w * 0.7
        btn_x = (w - btn_w) // 2
        
        for i, txt in enumerate(p["opcoes_embaralhadas"]):
            r = pygame.Rect(btn_x, btn_start_y + i * (btn_h + btn_spacing), btn_w, btn_h)
            btn = CyberButton(r, txt, layout['font_opcao'])
            current_buttons.append(btn)

    # Inicia primeira pergunta
    setup_question_ui(0)

    # LOOP PRINCIPAL
    while True:
        # WEB: Use dt fixo ou capado para evitar física explodindo
        dt = clock.tick(60) / 16.0
        
        # Shake Logic
        shake_x, shake_y = 0, 0
        if shake_amount > 0:
            shake_amount -= 0.5
            shake_x = random.randint(-int(shake_amount), int(shake_amount))
            shake_y = random.randint(-int(shake_amount), int(shake_amount))

        # 1. Background (Blit simples é rápido)
        screen.blit(layout['background'], (shake_x, shake_y))
        
        # 2. Partículas
        for p in bg_particles:
            p.update(dt)
            p.draw(screen)

        if pergunta_idx >= len(perguntas):
            audio_manager.play_sfx_if_exists("roleta")
            await show_pause_screen(screen, clock, "Fim do Show!", f"Saldo Final: {ScoreManager.get_score()}", theme="Show do Bilhão")
            return 0

        # 3. UI Estática (Título, Ícones)
        screen.blit(layout['title_surf'], (layout['title_rect'].x + shake_x, layout['title_rect'].y + shake_y))
        
        if layout['icon']:
            # Desenha ícones ao lado do título
            icon = layout['icon']
            il_pos = (layout['title_rect'].left - icon.get_width() - 20 + shake_x, layout['title_rect'].centery - icon.get_height()//2 + shake_y)
            ir_pos = (layout['title_rect'].right + 20 + shake_x, layout['title_rect'].centery - icon.get_height()//2 + shake_y)
            screen.blit(icon, il_pos)
            screen.blit(icon, ir_pos)

        # 4. Score
        draw_score_display(screen, ScoreManager.get_score(), layout['font_ui'], position="topright")

        # 5. Pergunta (Container Cacheado)
        # Header "PERGUNTA X/Y" (desenhado aqui pois precisa de posição absoluta)
        head_rect = pygame.Rect(current_container_rect.left + shake_x, current_container_rect.top - 30 + shake_y, 160, 30)
        pygame.draw.rect(screen, (255, 215, 0), head_rect, border_top_left_radius=5, border_top_right_radius=15)
        lbl = layout['font_ui'].render(f"PERGUNTA {pergunta_idx+1}/{len(perguntas)}", True, (10,10,10))
        screen.blit(lbl, (head_rect.x + 10, head_rect.y + 5))
        
        # Blit Container
        screen.blit(current_container_surf, (current_container_rect.x + shake_x, current_container_rect.y + shake_y))

        # 6. Botões
        mouse_pos = pygame.mouse.get_pos()
        for btn in current_buttons:
            # Estado do feedback
            fb_state = 0
            if feedback:
                if btn.text == feedback["correct_text"]:
                    fb_state = 1 # Correto
                elif btn.text == feedback["selected_text"] and not feedback["correto"]:
                    fb_state = 2 # Errado
            
            # Hover apenas se não houver feedback
            if not feedback:
                btn.check_hover(mouse_pos)
            
            btn.draw(screen, fb_state)

        # 7. Explosões
        for ep in explosion_particles[:]:
            ep.update()
            ep.draw(screen)
            if ep.life <= 0:
                explosion_particles.remove(ep)

        # 8. Feedback Overlay
        if feedback:
            # Overlay escuro
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            
            w, h = screen.get_size()
            msg_rect = pygame.Rect(0, 0, w*0.6, h*0.4)
            msg_rect.center = (w//2, h//2)
            
            color = (50, 255, 50) if feedback["correto"] else (255, 50, 50)
            pygame.draw.rect(screen, (20, 20, 30), msg_rect, border_radius=20)
            pygame.draw.rect(screen, color, msg_rect, 3, border_radius=20)
            
            res_txt = "EXCELENTE!" if feedback["correto"] else "ERROU!"
            t_res = layout['font_titulo'].render(res_txt, True, color)
            screen.blit(t_res, t_res.get_rect(center=(w//2, msg_rect.top + 50)))
            
            # Texto explicativo
            reason_area = msg_rect.inflate(-40, -100)
            reason_area.top += 60
            
            full_msg = feedback["correct_reason"]
            if not feedback["correto"]:
                full_msg = f"Resposta certa: {feedback['correct_text']}\n\n{full_msg}"
                
            draw_text_wrapped(screen, full_msg, layout['font_opcao'], (220, 220, 220), reason_area)

            # Timer Feedback
            if pygame.time.get_ticks() - feedback["start"] > FEEDBACK_DURATION:
                pergunta_idx += 1
                feedback = None
                if pergunta_idx < len(perguntas):
                    setup_question_ui(pergunta_idx)

        pygame.display.flip()
        
        # PONTO VITAL
        await asyncio.sleep(0)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    resize_assets(screen)
                    if pergunta_idx < len(perguntas):
                        setup_question_ui(pergunta_idx) # Recria layout se mudar tamanho
                elif event.key == pygame.K_ESCAPE:
                    return 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not feedback:
                for btn in current_buttons:
                    if btn.rect.collidepoint(event.pos):
                        # Trigger Explosão
                        for _ in range(20):
                            explosion_particles.append(ExplosionParticle(event.pos[0], event.pos[1], layout['font_particle']))
                        
                        # Lógica
                        acertou = (btn.text == perguntas[pergunta_idx]["texto_correto"])
                        if acertou:
                            ScoreManager.add_points(pontos_acerto)
                            audio_manager.play_sfx_if_exists("correto")
                        else:
                            ScoreManager.add_points(pontos_erro)
                            audio_manager.play_sfx_if_exists("errado")
                            shake_amount = 20
                        
                        feedback = {
                            "start": pygame.time.get_ticks(),
                            "correto": acertou,
                            "correct_text": perguntas[pergunta_idx]["texto_correto"],
                            "selected_text": btn.text,
                            "correct_reason": perguntas[pergunta_idx]["motivo_correto"]
                        }
                        # Renderiza frame de impacto imediato
                        pygame.display.flip()
                        await asyncio.sleep(0.05)
                        break
    return 0