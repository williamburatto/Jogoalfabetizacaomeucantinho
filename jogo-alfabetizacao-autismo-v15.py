"""
==============================================================================
JOGO DE ALFABETIZAÇÃO ADAPTATIVA PARA ALUNOS COM AUTISMO - VERSÃO 15 (FINAL)
==============================================================================
Esta versão implementa uma aplicação web e executável totalmente INTERATIVA (Streamlit + Python),
com suporte a 12 SUBFASES PROGRESSIVAS DE ALFABETIZAÇÃO, TRANSIÇÃO AUTOMÁTICA DE SUBFASES,
GESTÃO COMPLETA DE ALUNOS (CRIAR E EDITAR NOME), DICAS GRADUAIS EM 2 CAMADAS,
MOTOR FUZZY COGNITIVO (FCM), BANCO DE DADOS PERSISTENTE E DASHBOARDS DIFERENCIADOS
EM ABAS SEPARADAS PARA A FAMÍLIA E PARA O PROFESSOR COM RELATÓRIOS AUTOMÁTICOS DE ERROS E MELHORIAS.

Como Executar no VS Code / Navegador:
    streamlit run jogo-alfabetizacao-autismo-v15.py

Como Executar via Terminal Python (Geração Automática de Relatórios e Gráficos):
    python jogo-alfabetizacao-autismo-v15.py
"""

import os
import json
import time
import hashlib
import sys
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# 1. FUNÇÕES AUXILIARES DE RESOLUÇÃO DE CAMINHOS E DETECÇÃO DE AMBIENTE
# ==============================================================================


def resolve_image_path(filename):
    """Busca o arquivo de imagem nos diretórios possíveis com fallback seguro."""
    search_dirs = [
        "/workspace/scratch/v15",
        "/workspace/scratch",
        "/workspace/out",
        "/workspace/artifacts",
        "."
    ]
    for d in search_dirs:
        p = os.path.join(d, filename)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None

def is_streamlit_running():
    """Detecta se o script está sendo executado via Streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            return True
    except Exception:
        pass
    for arg in sys.argv:
        if "streamlit" in arg.lower():
            return True
    return False

# ==============================================================================
# 2. GERENCIADOR DE BANCO DE DADOS PERSISTENTE DOS ALUNOS
# ==============================================================================


class StudentDataManager:
    """Gerencia o cadastro, alteração e salvamento individual de histórico dos alunos."""
    def __init__(self, db_filename="student_database_v15.json"):
        self.db_filename = db_filename
        self.db_paths = [
            os.path.join("/workspace/scratch/v15", db_filename),
            os.path.join("/workspace/scratch", db_filename),
            os.path.join("/workspace/out", db_filename),
            db_filename
        ]
        self.students = {}
        self.load_db()

    def load_db(self):
        loaded = False
        for p in self.db_paths:
            if os.path.exists(p) and os.path.getsize(p) > 0:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        self.students = json.load(f)
                    loaded = True
                    break
                except Exception:
                    pass
        if not loaded or not self.students:
            # Perfil padrão de demonstração
            self.students = {
                "João Silva": {
                    "student_id": "ALUNO_01",
                    "student_name": "João Silva",
                    "total_play_time_min": 45,
                    "ability_score": 0.65,
                    "session_logs": [
                        {"timestamp": "10:00", "fase": "Fase 1", "subfase": "Subfase 1.1", "item": "BOLA", "correto": True, "precisao": 100.0, "tempo_resposta": 7.5, "dicas_usadas": 0, "categoria": "Fonemas Iniciais", "materia": "Português"},
                        {"timestamp": "10:02", "fase": "Fase 1", "subfase": "Subfase 1.2", "item": "MAPA", "correto": True, "precisao": 100.0, "tempo_resposta": 6.0, "dicas_usadas": 0, "categoria": "Fonemas Nasais", "materia": "Português"},
                        {"timestamp": "10:05", "fase": "Fase 1", "subfase": "Subfase 1.3", "item": "RIO", "correto": False, "precisao": 0.0, "tempo_resposta": 18.0, "dicas_usadas": 2, "categoria": "Fonemas Vibrantes", "materia": "Português"},
                        {"timestamp": "10:08", "fase": "Fase 1", "subfase": "Subfase 1.3", "item": "RIO", "correto": True, "precisao": 100.0, "tempo_resposta": 9.0, "dicas_usadas": 1, "categoria": "Fonemas Vibrantes", "materia": "Português"},
                        {"timestamp": "10:12", "fase": "Fase 2", "subfase": "Subfase 2.1", "item": "MAPA", "correto": True, "precisao": 100.0, "tempo_resposta": 10.0, "dicas_usadas": 0, "categoria": "Sílabas Dissílabas", "materia": "Português"},
                        {"timestamp": "10:15", "fase": "Fase 2", "subfase": "Subfase 2.2", "item": "CASA", "correto": False, "precisao": 0.0, "tempo_resposta": 15.0, "dicas_usadas": 1, "categoria": "Sílabas Cotidiano", "materia": "Português"},
                        {"timestamp": "10:18", "fase": "Fase 2", "subfase": "Subfase 2.3", "item": "CADERNO", "correto": True, "precisao": 100.0, "tempo_resposta": 12.0, "dicas_usadas": 0, "categoria": "Sílabas Trissílabas Escola", "materia": "Português"},
                        {"timestamp": "10:22", "fase": "Fase 3", "subfase": "Subfase 3.1", "item": "O RIO É BONITO", "correto": True, "precisao": 100.0, "tempo_resposta": 11.0, "dicas_usadas": 0, "categoria": "Leitura Frasal", "materia": "Geografia"}
                    ]
                },
                "Maria Souza": {
                    "student_id": "ALUNO_02",
                    "student_name": "Maria Souza",
                    "total_play_time_min": 30,
                    "ability_score": 0.85,
                    "session_logs": [
                        {"timestamp": "11:00", "fase": "Fase 1", "subfase": "Subfase 1.1", "item": "BOLA", "correto": True, "precisao": 100.0, "tempo_resposta": 5.0, "dicas_usadas": 0, "categoria": "Fonemas Iniciais", "materia": "Português"},
                        {"timestamp": "11:03", "fase": "Fase 2", "subfase": "Subfase 2.1", "item": "MAPA", "correto": True, "precisao": 100.0, "tempo_resposta": 6.5, "dicas_usadas": 0, "categoria": "Sílabas Dissílabas", "materia": "Português"},
                        {"timestamp": "11:06", "fase": "Fase 2", "subfase": "Subfase 2.5", "item": "ALFABETO", "correto": True, "precisao": 100.0, "tempo_resposta": 9.0, "dicas_usadas": 0, "categoria": "Sílabas Complexas", "materia": "Português"}
                    ]
                }
            }
            self.save_db()

    def save_db(self):
        for p in self.db_paths:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(self.students, f, ensure_ascii=False, indent=4)
            except Exception:
                pass

    def get_student_names(self):
        return list(self.students.keys())

    def get_student(self, name):
        if name not in self.students:
            self.create_student(name)
        return self.students[name]

    def create_student(self, name):
        if not name or name.strip() == "":
            return False
        clean_name = name.strip()
        if clean_name not in self.students:
            self.students[clean_name] = {
                "student_id": f"ALUNO_{len(self.students)+1:02d}",
                "student_name": clean_name,
                "total_play_time_min": 0,
                "ability_score": 0.50,
                "session_logs": []
            }
            self.save_db()
            return True
        return False

    def rename_student(self, old_name, new_name):
        if not new_name or new_name.strip() == "" or old_name not in self.students:
            return False
        clean_new = new_name.strip()
        if clean_new in self.students and clean_new != old_name:
            return False
        data = self.students.pop(old_name)
        data["student_name"] = clean_new
        self.students[clean_new] = data
        self.save_db()
        return True

    def add_log(self, student_name, log_entry):
        st_data = self.get_student(student_name)
        st_data["session_logs"].append(log_entry)
        st_data["total_play_time_min"] += int(log_entry.get("tempo_resposta", 10) / 60) + 1
        st_data["ability_score"] = log_entry.get("habilidade_estimada", 50.0) / 100.0
        self.save_db()

# ==============================================================================
# 3. MOTOR FUZZY COGNITIVO (FCM), FLOW THEORY E PROJEÇÃO TEMPORAL
# ==============================================================================


class FuzzyCognitiveEngine:
    """Motor adaptativo baseado em FCMs para calibração dinâmica e diagnóstico."""
    def __init__(self, student_id="ALUNO_01", student_name="João Silva"):
        self.student_id = student_id
        self.student_name = student_name
        self.ability_score = 0.50
        self.challenge_level = 0.50
        self.sensory_overload_risk = 0.0
        self.consecutive_errors = 0
        self.session_logs = []
        self.alerts = []

    def load_from_student_data(self, student_data):
        self.student_name = student_data.get("student_name", "João Silva")
        self.student_id = student_data.get("student_id", "ALUNO_01")
        self.ability_score = student_data.get("ability_score", 0.50)
        self.session_logs = student_data.get("session_logs", [])

    def process_interaction(self, phase, subphase, item_name, is_correct, response_time_sec, hints_used, category, subject):
        if is_correct:
            gain = 0.10 if hints_used == 0 else 0.05
            self.ability_score = min(1.0, self.ability_score + gain)
            self.consecutive_errors = 0
        else:
            self.ability_score = max(0.10, self.ability_score - 0.08)
            self.consecutive_errors += 1

        self.challenge_level = 0.65 * self.challenge_level + 0.35 * self.ability_score

        if response_time_sec > 20 or hints_used >= 2 or self.consecutive_errors >= 2:
            self.sensory_overload_risk = min(1.0, self.sensory_overload_risk + 0.20)
        else:
            self.sensory_overload_risk = max(0.0, self.sensory_overload_risk - 0.10)

        if self.consecutive_errors >= 2 or hints_used >= 2:
            alert_msg = f"Aviso de Mediação: {self.student_name} hesitou no item '{item_name}' ({subphase}). Sugerida intervenção direta."
            if alert_msg not in self.alerts:
                self.alerts.append(alert_msg)

        log_entry = {
            'timestamp': time.strftime("%H:%M:%S"),
            'fase': phase,
            'subfase': subphase,
            'item': item_name,
            'categoria': category,
            'materia': subject,
            'correto': is_correct,
            'precisao': 100.0 if is_correct else 0.0,
            'tempo_resposta': response_time_sec,
            'dicas_usadas': hints_used,
            'habilidade_estimada': self.ability_score * 100.0,
            'desafio_ajustado': self.challenge_level * 100.0,
            'risco_sensorial': self.sensory_overload_risk * 100.0
        }
        self.session_logs.append(log_entry)
        return log_entry

    def get_literacy_stage_and_projection(self):
        A = self.ability_score
        total_tasks = len(self.session_logs)
        avg_time = np.mean([log['tempo_resposta'] for log in self.session_logs]) if total_tasks > 0 else 10.0
        avg_acc = np.mean([log['precisao'] for log in self.session_logs]) if total_tasks > 0 else 80.0

        if A < 0.40:
            stage_title = "Estágio 1: Consciência Fonêmica Inicial"
            next_stage = "Estágio 2: Síntese Silábica & Leitura Guiada"
            est_minutes = int(30 * (0.40 - A) / 0.1) + 10
            rec = "Priorizar associação de sons (fonemas) com figuras e letras em destaque."
        elif A < 0.70:
            stage_title = "Estágio 2: Síntese Silábica e Formação de Palavras"
            next_stage = "Estágio 3: Vocabulário do Cotidiano & Escola"
            est_minutes = int(30 * (0.70 - A) / 0.1) + 10
            rec = "Praticar junções de sílabas móveis (dissílabas e trissílabas)."
        elif A < 0.90:
            stage_title = "Estágio 3: Vocabulário Ampliado da Escola e Casa"
            next_stage = "Estágio 4: Leitura Fluente & Resolutor Interdisciplinar"
            est_minutes = int(30 * (0.90 - A) / 0.1) + 5
            rec = "Expandir leitura de palavras polissílabas e pequenas frases."
        else:
            stage_title = "Estágio 4: Leitura Fluente & Resolutor Interdisciplinar"
            next_stage = "Alfabetização Plena Concluída com Sucesso! 🎉"
            est_minutes = 0
            rec = "Fortalecer compreensão leitora e empatia em situações sociais."

        sessions = max(0, int(np.ceil(est_minutes / 15.0)))
        efficiency = min(150.0, max(60.0, (avg_acc / 100.0) * (15.0 / max(5.0, avg_time)) * 100.0))

        return {
            'stage_title': stage_title,
            'next_stage': next_stage,
            'est_minutes_left': est_minutes,
            'sessions_left': sessions,
            'efficiency_rate': round(efficiency, 1),
            'recommendation': rec
        }

# ==============================================================================
# 4. MATRIZ PEDAGÓGICA (12 SUBFASES PROGRESSIVAS)
# ==============================================================================


class GameContentRepository:
    """Contém as 12 Subfases do jogo organizadas em 3 Macro-Fases."""

    SUBFASES = [
        # MACRO-FASE 1: FONEMAS & ALFABETO
        {
            "fase": "Fase 1: Fonemas & Alfabeto",
            "subfase": "Subfase 1.1: Fonemas Iniciais Básicos",
            "fonema": "/b/", "letra": "B", "imagem": "🏀", "palavra": "BOLA",
            "opcoes": ["B", "M", "R", "C"],
            "dica_visual": "✨ A letra B brilha em DOURADO! Pense em BOLA 🏀",
            "dica_sonora": "🗣️ Junte os dois lábios suavemente, solte o ar e faça /b/ - BOLA!",
            "materia": "Português", "categoria": "Consciência Fonêmica"
        },
        {
            "fase": "Fase 1: Fonemas & Alfabeto",
            "subfase": "Subfase 1.2: Fonemas Nasais e Suaves",
            "fonema": "/m/", "letra": "M", "imagem": "🗺️", "palavra": "MAPA",
            "opcoes": ["P", "M", "T", "S"],
            "dica_visual": "✨ A letra M possui duas montanhas brilhantes! Pense em MAPA 🗺️",
            "dica_sonora": "🗣️ Pressione os lábios e faça o som ressonar pelo nariz: /m/ - MAPA!",
            "materia": "Português", "categoria": "Consciência Fonêmica"
        },
        {
            "fase": "Fase 1: Fonemas & Alfabeto",
            "subfase": "Subfase 1.3: Fonemas Vibrantes e Fricativos",
            "fonema": "/r/", "letra": "R", "imagem": "🌊", "palavra": "RIO",
            "opcoes": ["L", "F", "R", "V"],
            "dica_visual": "✨ A letra R brilha com o fluxo da água! Pense em RIO 🌊",
            "dica_sonora": "🗣️ Faça o som vibrar na garganta: /r/ - RIO!",
            "materia": "Geografia", "categoria": "Consciência Fonêmica"
        },
        {
            "fase": "Fase 1: Fonemas & Alfabeto",
            "subfase": "Subfase 1.4: Fonemas em Palavras Trissílabas",
            "fonema": "/s/", "letra": "S", "imagem": "🧼", "palavra": "SABÃO",
            "opcoes": ["Z", "S", "X", "J"],
            "dica_visual": "✨ A letra S tem o formato de uma cobra sorridente! Pense em SABÃO 🧼",
            "dica_sonora": "🗣️ Faça o som do sopro contínuo: /s/ - SABÃO!",
            "materia": "Português", "categoria": "Consciência Fonêmica"
        },

        # MACRO-FASE 2: SÍNTESE SILÁBICA & FORMAÇÃO DE PALAVRAS
        {
            "fase": "Fase 2: Síntese Silábica",
            "subfase": "Subfase 2.1: Palavras Dissílabas Simples",
            "palavra": "MAPA", "imagem": "🗺️",
            "silabas_corretas": ["MA", "PA"],
            "silabas_embaralhadas": ["PA", "MA", "BO", "LA"],
            "dica_visual": "✨ A primeira sílaba é MA (de Maria / Mapa).",
            "dica_sonora": "🗣️ Junte MA 🧩 com PA 🧩 para formar a palavra MAPA 🗺️!",
            "materia": "Geografia", "categoria": "Síntese Silábica"
        },
        {
            "fase": "Fase 2: Síntese Silábica",
            "subfase": "Subfase 2.2: Palavras Dissílabas do Cotidiano",
            "palavra": "CASA", "imagem": "🏠",
            "silabas_corretas": ["CA", "SA"],
            "silabas_embaralhadas": ["SA", "CA", "TO", "MA"],
            "dica_visual": "✨ A primeira sílaba é CA (de Casa).",
            "dica_sonora": "🗣️ Junte CA 🧩 com SA 🧩 para formar CASA 🏠!",
            "materia": "Português", "categoria": "Síntese Silábica"
        },
        {
            "fase": "Fase 2: Síntese Silábica",
            "subfase": "Subfase 2.3: Palavras Trissílabas da Escola",
            "palavra": "CADERNO", "imagem": "📘",
            "silabas_corretas": ["CA", "DER", "NO"],
            "silabas_embaralhadas": ["NO", "CA", "DER", "LA"],
            "dica_visual": "✨ As sílabas são CA + DER + NO (3 partes).",
            "dica_sonora": "🗣️ Diga pausadamente: CA... DER... NO 📘!",
            "materia": "Português", "categoria": "Síntese Silábica"
        },
        {
            "fase": "Fase 2: Síntese Silábica",
            "subfase": "Subfase 2.4: Palavras Trissílabas da Natureza",
            "palavra": "ÁRVORE", "imagem": "🌳",
            "silabas_corretas": ["ÁR", "VO", "RE"],
            "silabas_embaralhadas": ["VO", "ÁR", "RE", "TA"],
            "dica_visual": "✨ Primeira sílaba forte: ÁR.",
            "dica_sonora": "🗣️ Junte ÁR + VO + RE para formar ÁRVORE 🌳!",
            "materia": "Geografia", "categoria": "Síntese Silábica"
        },
        {
            "fase": "Fase 2: Síntese Silábica",
            "subfase": "Subfase 2.5: Palavras Polissílabas e Complexas",
            "palavra": "ALFABETO", "imagem": "🔤",
            "silabas_corretas": ["AL", "FA", "BE", "TO"],
            "silabas_embaralhadas": ["BE", "AL", "TO", "FA"],
            "dica_visual": "✨ Palavra de 4 partes: AL + FA + BE + TO.",
            "dica_sonora": "🗣️ Articule cada pedaço: AL-FA-BE-TO 🔤!",
            "materia": "Português", "categoria": "Síntese Silábica"
        },

        # MACRO-FASE 3: LEITURA FRASAL & COGNIÇÃO INTERDISCIPLINAR
        {
            "fase": "Fase 3: Leitura & Cognição",
            "subfase": "Subfase 3.1: Leitura de Frases Simples",
            "frase_alvo": "O RIO É BONITO", "imagem": "🌊",
            "blocos_corretos": ["O", "RIO", "É", "BONITO"],
            "blocos_embaralhados": ["BONITO", "O", "É", "RIO"],
            "dica_visual": "✨ Comece com a letra inicial 'O' e depois 'RIO'.",
            "dica_sonora": "🗣️ Leia com calma: O... RIO... É... BONITO 🌊!",
            "materia": "Geografia", "categoria": "Leitura Frasal"
        },
        {
            "fase": "Fase 3: Leitura & Cognição",
            "subfase": "Subfase 3.2: Frases Complexas de Geografia e História",
            "frase_alvo": "O MAPA MOSTRA O CASTELO DO REI", "imagem": "👑",
            "blocos_corretos": ["O", "MAPA", "MOSTRA", "O", "CASTELO"],
            "blocos_embaralhados": ["MOSTRA", "O", "MAPA", "CASTELO", "O"],
            "dica_visual": "✨ O MAPA vem primeiro, indicando o lugar.",
            "dica_sonora": "🗣️ Ordene o pensamento: O MAPA MOSTRA O CASTELO 👑!",
            "materia": "História", "categoria": "Leitura Frasal"
        },
        {
            "fase": "Fase 3: Leitura & Cognição",
            "subfase": "Subfase 3.3: Historinhas Sociais & Empatia Escolar",
            "situacao": "Um colega perdeu o lápis de cor na sala de aula e ficou triste. O que podemos fazer?",
            "imagem": "🤝",
            "opcoes": ["Oferecer um lápis emprestado", "Ignorar o colega", "Rir do colega", "Esconder os lápis"],
            "resposta_correta": "Oferecer um lápis emprestado",
            "dica_visual": "✨ A atitude empática ajuda o amigo a sorrir.",
            "dica_sonora": "🗣️ Ajudar e compartilhar fortalece a amizade na escola 💙!",
            "materia": "História", "categoria": "Cognição Social"
        }
    ]

# ==============================================================================
# 5. GERADOR DE DASHBOARDS E RELATÓRIOS EM GRÁFICOS (PNG)
# ==============================================================================


class AnalyticsDashboardGenerator:
    @staticmethod
    def generate_student_dashboard(session_logs, engine, student_name="João Silva", output_path="/workspace/scratch/v15/dashboard-progresso-autismo-v15.png"):
        df = pd.DataFrame(session_logs)
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'PAINEL DA FAMÍLIA & AUTORREFLEXÃO - {student_name.upper()}', fontsize=16, fontweight='bold', color='#1B4F72')

        # Subplot 1: Precisão por Subfase
        if not df.empty and 'subfase' in df.columns:
            sub_perf = df.groupby('subfase')['precisao'].mean()
            colors = ['#2ECC71' if v >= 80 else '#3498DB' if v >= 60 else '#E67E22' for v in sub_perf.values]
            bars = axes[0, 0].barh([s.replace('Subfase ', '') for s in sub_perf.index], sub_perf.values, color=colors)
            axes[0, 0].set_xlim(0, 100)
            axes[0, 0].set_title('1. Desempenho por Subfase (%)', fontsize=12, fontweight='bold')
            for bar in bars:
                w = bar.get_width()
                axes[0, 0].text(w + 1, bar.get_y() + bar.get_height()/2, f'{int(w)}%', va='center', fontweight='bold', fontsize=9)
        else:
            axes[0, 0].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 2: Curva de Fluxo
        if not df.empty and 'habilidade_estimada' in df.columns:
            rounds = list(range(1, len(df) + 1))
            axes[0, 1].plot(rounds, df['habilidade_estimada'], marker='o', color='#2ECC71', label='Habilidade do Aluno', linewidth=2.5)
            axes[0, 1].plot(rounds, df['desafio_ajustado'], marker='s', color='#E74C3C', linestyle='--', label='Desafio Ajustado (FCM)', linewidth=2)
            axes[0, 1].set_ylim(0, 100)
            axes[0, 1].set_title('2. Curva de Aprendizado e Desafio (FCM)', fontsize=12, fontweight='bold')
            axes[0, 1].legend(loc='lower right')
        else:
            axes[0, 1].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 3: Distribuição de Autonomia e Dicas
        if not df.empty and 'dicas_usadas' in df.columns:
            d_counts = df['dicas_usadas'].value_counts()
            labels = ['Sem Dicas (Autônomo)', 'Camada 1 (Visual)', 'Camada 2 (Sonora)']
            vals = [d_counts.get(0, 0), d_counts.get(1, 0), d_counts.get(2, 0)]
            if sum(vals) > 0:
                axes[1, 0].pie(vals, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#2ECC71', '#F39C12', '#E74C3C'])
            axes[1, 0].set_title('3. Nível de Autonomia & Suporte de Dicas', fontsize=12, fontweight='bold')
        else:
            axes[1, 0].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 4: Projeção de Tempo e Recomendação Família
        proj = engine.get_literacy_stage_and_projection()
        axes[1, 1].axis('off')
        info_family = (
            f"🏠 PAINEL DE ACOMPANHAMENTO DA FAMÍLIA:\n\n"
            f"• Estágio Atual: {proj['stage_title']}\n"
            f"• Próxima Conquista: {proj['next_stage']}\n"
            f"• Tempo Estimado de Jogo: ~{proj['est_minutes_left']} min ({proj['sessions_left']} sessões curtas)\n"
            f"• Eficiência do Aprendizado: {proj['efficiency_rate']}%\n\n"
            f"💡 ORIENTAÇÃO PARA PRÁTICA EM CASA:\n"
            f"{proj['recommendation']}"
        )
        axes[1, 1].text(0.05, 0.95, info_family, transform=axes[1, 1].transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#EAFAF1', alpha=0.9))
        axes[1, 1].set_title('4. Projeção de Evolução Leitora', fontsize=12, fontweight='bold')

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path

    @staticmethod
    def generate_teacher_dashboard(engine, auth_system, student_name="João Silva", output_path="/workspace/scratch/v15/dashboard-professor-autismo-v15.png"):
        df = pd.DataFrame(engine.session_logs)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        title_text = f"PORTAL EXCLUSIVO DO PROFESSOR - Aluno: {student_name.upper()}"
        fig.suptitle(title_text, fontsize=14, fontweight='bold', color='#6C3483')

        # Subplot 1: Desempenho por Matéria
        if not df.empty and 'materia' in df.columns:
            mat_perf = df.groupby('materia')['precisao'].mean()
            axes[0, 0].bar(mat_perf.index, mat_perf.values, color=['#3498DB', '#E67E22', '#2ECC71'])
            axes[0, 0].set_ylim(0, 100)
            axes[0, 0].set_title('1. Desempenho por Disciplina (%)', fontsize=12, fontweight='bold')
        else:
            axes[0, 0].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 2: Erros / Hesitações por Subfase
        if not df.empty and 'subfase' in df.columns:
            df['erro_bin'] = df['correto'].apply(lambda x: 0 if x else 1)
            err_sub = df.groupby('subfase')['erro_bin'].sum()
            axes[0, 1].bar([s.replace('Subfase ', '') for s in err_sub.index], err_sub.values, color='#E74C3C')
            axes[0, 1].set_title('2. Total de Erros / Hesitações por Subfase', fontsize=12, fontweight='bold')
        else:
            axes[0, 1].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 3: Nível de Risco Sensorial (FCM)
        if not df.empty and 'risco_sensorial' in df.columns:
            rounds = list(range(1, len(df) + 1))
            axes[1, 0].plot(rounds, df['risco_sensorial'], marker='d', color='#C0392B', linewidth=2)
            axes[1, 0].axhline(y=50, color='gray', linestyle=':', label='Limiar Confortável')
            axes[1, 0].set_ylim(0, 100)
            axes[1, 0].set_title('3. Estresse / Carga Sensorial FCM (%)', fontsize=12, fontweight='bold')
        else:
            axes[1, 0].text(0.5, 0.5, "Aguardando exercícios...", ha='center', va='center')

        # Subplot 4: Diagnóstico Pedagógico Docente
        proj = engine.get_literacy_stage_and_projection()
        axes[1, 1].axis('off')
        info_doc = (
            f"👨‍🏫 DIAGNÓSTICO DOCENTE EM TEMPO REAL:\n\n"
            f"• Estágio Diagnosticado: {proj['stage_title']}\n"
            f"• Habilidade Estimada: {engine.ability_score*100:.1f}%\n"
            f"• Risco Sensorial Atual: {engine.sensory_overload_risk*100:.1f}%\n"
            f"• Link da Turma: {auth_system.student_link}\n\n"
            f"⚠️ ALERTAS DE MEDIAÇÃO REGISTRADOS:\n"        )
        if engine.alerts:
            for a in engine.alerts[-2:]:
                info_doc += f"  - {a}\n"
        else:
            info_doc += "  - Nenhum bloqueio crítico detectado.\n"

        info_doc += f"\n• ORIENTAÇÃO PEDAGÓGICA: {proj['recommendation']}"
        axes[1, 1].text(0.05, 0.95, info_doc, transform=axes[1, 1].transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#F4ECF7', alpha=0.9))
        axes[1, 1].set_title('4. Diagnóstico e Alertas Pedagógicos', fontsize=12, fontweight='bold')

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path

# ==============================================================================.
# 6. MODO APLICAÇÃO INTERATIVA WEB (STREAMLIT)
# ==============================================================================


def run_streamlit_app():
    import streamlit as st

    st.set_page_config(page_title="Jogo de Alfabetização Adaptativa v15", layout="wide", page_icon="🧩")

    # Estilização CSS para cartões ilustrativos gigantes e animações
    st.markdown("""
    <style>
        .big-card {
            background-color: #F0F3F4;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            border: 4px solid #3498DB;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        .big-emoji {
            font-size: 80px;
            margin: 10px 0;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.08); }
            100% { transform: scale(1); }
        }
        .glow-visual {
            background-color: #FEF9E7;
            border: 4px solid #F1C40F;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 0 20px #F1C40F;
        }
        .articulatory-hint {
            background-color: #EBF5FB;
            border: 4px solid #3498DB;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Inicialização do Banco de Dados
    if 'db' not in st.session_state:
        st.session_state.db = StudentDataManager()

    db = st.session_state.db

    # Barra Lateral - Gestão de Alunos e Navegação
    st.sidebar.title("👥 Gestão do Estudante")
    student_list = db.get_student_names()

    if 'active_student' not in st.session_state:
        st.session_state.active_student = student_list[0] if student_list else "João Silva"

    selected_student = st.sidebar.selectbox(
        "Selecione o Aluno Ativo:",
        student_list,
        index=student_list.index(st.session_state.active_student) if st.session_state.active_student in student_list else 0
    )
    st.session_state.active_student = selected_student

    # Formulários de Criar / Editar Aluno
    with st.sidebar.expander("➕ Criar Novo Aluno"):
        new_name_in = st.text_input("Nome do Novo Aluno:", key="new_st_input")
        if st.button("Cadastrar Aluno"):
            if db.create_student(new_name_in):
                st.session_state.active_student = new_name_in.strip()
                st.success(f"Aluno '{new_name_in}' cadastrado!")
                st.rerun()
            else:
                st.error("Nome inválido ou já existente.")

    with st.sidebar.expander("✏️ Editar Nome do Aluno"):
        edit_name_in = st.text_input("Novo Nome:", value=st.session_state.active_student, key="edit_st_input")
        if st.button("Salvar Alteração"):
            if db.rename_student(st.session_state.active_student, edit_name_in):
                st.session_state.active_student = edit_name_in.strip()
                st.success("Nome alterado com sucesso!")
                st.rerun()
            else:
                st.error("Não foi possível alterar o nome.")

    # Inicialização do Motor para o Aluno Ativo
    student_data = db.get_student(st.session_state.active_student)
    if 'engine' not in st.session_state or st.session_state.engine.student_name != st.session_state.active_student:
        engine = FuzzyCognitiveEngine()
        engine.load_from_student_data(student_data)
        st.session_state.engine = engine
    else:
        engine = st.session_state.engine

    if 'active_subphase_idx' not in st.session_state:
        st.session_state.active_subphase_idx = 0
    if 'built_silabas' not in st.session_state:
        st.session_state.built_silabas = []
    if 'built_frase' not in st.session_state:
        st.session_state.built_frase = []
    if 'hints_count' not in st.session_state:
        st.session_state.hints_count = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    if 'auth' not in st.session_state:
        st.session_state.auth = type('TeacherAuth', (), {
            'verify_password': lambda self, p: p == 'prof123',
            'student_link': 'https://jogo-alfabetizacao-autismo.edu.br/aluno?turma=ef01'
        })()

    auth = st.session_state.auth

    st.sidebar.markdown("---")
    st.sidebar.title("🧩 Modos do Sistema")
    mode = st.sidebar.radio("Escolha a visualização:", [
        "🎮 Modo Aluno (Jogo Interativo Touch)",
        "🏠 Dashboard dos Pais / Família",
        "👨‍🏫 Portal do Professor (Acesso Restrito)"
    ])

    # --------------------------------------------------------------------------
    # MODO 1: JOGO INTERATIVO TOUCH (SEM TECLADO, PASSAGEM AUTOMÁTICA)
    # --------------------------------------------------------------------------
    if mode == "🎮 Modo Aluno (Jogo Interativo Touch)":
        st.title(f"🎮 Jogo de Alfabetização Adaptativa — Estudante: {st.session_state.active_student}")
        st.caption("Interface 100% visual e adaptada para toque na tela / cliques diretos do mouse.")

        subfases_list = GameContentRepository.SUBFASES
        curr_idx = st.session_state.active_subphase_idx % len(subfases_list)
        item = subfases_list[curr_idx]

        st.progress((curr_idx + 1) / len(subfases_list), text=f"Progresso: Subfase {curr_idx + 1} de {len(subfases_list)} ({item['subfase']})")

        # Exibição de Dicas Graduais de 2 Camadas
        if st.session_state.hints_count == 1:
            st.markdown(f"<div class='glow-visual'>{item.get('dica_visual', 'Observe o destaque na imagem!')}</div>", unsafe_allow_html=True)
        elif st.session_state.hints_count >= 2:
            st.markdown(f"<div class='articulatory-hint'>{item.get('dica_sonora', 'Preste atenção no som!')}</div>", unsafe_allow_html=True)

        # MACRO-FASE 1: FONEMAS
        if "Fase 1" in item["fase"]:
            st.subheader(f"📌 {item['subfase']}")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"<div class='big-card'><div class='big-emoji'>{item['imagem']}</div><h2>Fonema: {item['fonema']}</h2><h3>{item['palavra']}</h3></div>", unsafe_allow_html=True)
                
                # Reprodução do Áudio vocal via Web Speech API
                audio_script = f"""
                <script>
                    function playAudio() {{
                        var msg = new SpeechSynthesisUtterance('{item['palavra']}... Som da letra: {item['fonema']}');
                        msg.lang = 'pt-BR';
                        window.speechSynthesis.speak(msg);
                    }}
                </script>
                <button onclick="playAudio()" style="background-color:#2ECC71; color:white; font-size:20px; padding:12px 24px; border-radius:12px; border:none; cursor:pointer; width:100%;">🔊 Ouvir Som do Fonema</button>
                """
                st.components.v1.html(audio_script, height=70)

            with c2:
                st.markdown("### Toque na Letra que corresponde ao Som:")
                cols = st.columns(len(item['opcoes']))
                for idx, opt in enumerate(item['opcoes']):
                    if cols[idx].button(f"Letra {opt}", key=f"f1_btn_{opt}_{curr_idx}", use_container_width=True):
                        elapsed = time.time() - st.session_state.start_time
                        is_corr = (opt == item['letra'])
                        log_e = engine.process_interaction(item['fase'], item['subfase'], item['palavra'], is_corr, elapsed, st.session_state.hints_count, item['categoria'], item['materia'])
                        db.add_log(st.session_state.active_student, log_e)

                        if is_corr:
                            st.toast("🎉 Excelente! Você acertou! Avançando para a próxima subfase...", icon="✨")
                            st.session_state.active_subphase_idx += 1
                            st.session_state.hints_count = 0
                            st.session_state.start_time = time.time()
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error("Ops, tente novamente com carinho!")
                            st.session_state.hints_count += 1

                if st.button("❓ Pedir Pista de Ajuda", key="f1_hint_btn"):
                    st.session_state.hints_count += 1
                    st.rerun()

        # MACRO-FASE 2: SÍNTESE SILÁBICA
        elif "Fase 2" in item["fase"]:
            st.subheader(f"🧩 {item['subfase']}")
            st.markdown(f"<div class='big-card'><div class='big-emoji'>{item['imagem']}</div><h2>Monte a palavra: {item['palavra']}</h2></div>", unsafe_allow_html=True)

            st.markdown("### Sua construção por toques:")
            current_build_str = " ➕ ".join([f"[{s}]" for s in st.session_state.built_silabas]) if st.session_state.built_silabas else "(Toque nas sílabas abaixo na ordem correta)"
            st.info(f"### {current_build_str}")

            cols_sil = st.columns(len(item['silabas_embaralhadas']))
            for idx, sil in enumerate(item['silabas_embaralhadas']):
                if cols_sil[idx].button(f"Sílaba [{sil}]", key=f"f2_sil_{sil}_{idx}_{curr_idx}", use_container_width=True):
                    st.session_state.built_silabas.append(sil)
                    st.rerun()

            cb1, cb2 = st.columns(2)
            if cb1.button("✅ Confirmar Palavra", key="f2_check", use_container_width=True):
                elapsed = time.time() - st.session_state.start_time
                is_corr = (st.session_state.built_silabas == item['silabas_corretas'])
                log_e = engine.process_interaction(item['fase'], item['subfase'], item['palavra'], is_corr, elapsed, st.session_state.hints_count, item['categoria'], item['materia'])
                db.add_log(st.session_state.active_student, log_e)

                if is_corr:
                    st.toast(f"🌟 Fantástico! Você formou {item['palavra']}! Avançando automaticamente...", icon="🎉")
                    st.session_state.active_subphase_idx += 1
                    st.session_state.built_silabas = []
                    st.session_state.hints_count = 0
                    st.session_state.start_time = time.time()
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error("A ordem das sílabas não está correta. Tente organizar novamente!")
                    st.session_state.built_silabas = []
                    st.session_state.hints_count += 1

            if cb2.button("🔄 Limpar Sílabas", key="f2_clear", use_container_width=True):
                st.session_state.built_silabas = []
                st.rerun()

        # MACRO-FASE 3: LEITURA FRASAL & COGNIÇÃO
        elif "Fase 3" in item["fase"]:
            st.subheader(f"📖 {item['subfase']}")
            if "frase_alvo" in item:
                st.markdown(f"<div class='big-card'><div class='big-emoji'>{item['imagem']}</div><h2>Ordene a Frase: {item['frase_alvo']}</h2></div>", unsafe_allow_html=True)
                st.info(" ".join([f"[{b}]" for b in st.session_state.built_frase]) if st.session_state.built_frase else "(Toque nos blocos abaixo)")

                cols4 = st.columns(len(item['blocos_embaralhados']))
                for idx, blk in enumerate(item['blocos_embaralhados']):
                    if cols4[idx].button(f"[{blk}]", key=f"f3_blk_{blk}_{idx}_{curr_idx}", use_container_width=True):
                        st.session_state.built_frase.append(blk)
                        st.rerun()

                c_f1, c_f2 = st.columns(2)
                if c_f1.button("✅ Validar Frase", key="f3_check_f", use_container_width=True):
                    elapsed = time.time() - st.session_state.start_time
                    is_corr = (st.session_state.built_frase == item['blocos_corretos'])
                    log_e = engine.process_interaction(item['fase'], item['subfase'], item['frase_alvo'], is_corr, elapsed, st.session_state.hints_count, item['categoria'], item['materia'])
                    db.add_log(st.session_state.active_student, log_e)

                    if is_corr:
                        st.toast("👏 Frase perfeita! Avançando para a próxima subfase...", icon="🌟")
                        st.session_state.active_subphase_idx += 1
                        st.session_state.built_frase = []
                        st.session_state.hints_count = 0
                        st.session_state.start_time = time.time()
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Observe a ordem das palavras e tente novamente!")
                        st.session_state.built_frase = []
                        st.session_state.hints_count += 1

                if c_f2.button("🔄 Limpar Frase", key="f3_clear_f", use_container_width=True):
                    st.session_state.built_frase = []
                    st.rerun()

            elif "situacao" in item:
                st.markdown(f"<div class='big-card'><div class='big-emoji'>{item['imagem']}</div><h3>{item['situacao']}</h3></div>", unsafe_allow_html=True)
                for idx, opt in enumerate(item['opcoes']):
                    if st.button(f"Atitude {idx+1}: {opt}", key=f"f3_soc_{idx}_{curr_idx}", use_container_width=True):
                        elapsed = time.time() - st.session_state.start_time
                        is_corr = (opt == item['resposta_correta'])
                        log_e = engine.process_interaction(item['fase'], item['subfase'], "Empatia Escolar", is_corr, elapsed, st.session_state.hints_count, item['categoria'], item['materia'])
                        db.add_log(st.session_state.active_student, log_e)

                        if is_corr:
                            st.toast("💙 Linda atitude empática! Você concluiu todas as subfases!", icon="🎉")
                            st.session_state.active_subphase_idx += 1
                            st.session_state.hints_count = 0
                            st.session_state.start_time = time.time()
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error("Pense em como ajudar o colega com carinho!")
                            st.session_state.hints_count += 1

    # --------------------------------------------------------------------------
    # MODO 2: DASHBOARD DOS PAIS / FAMÍLIA (COM RELATÓRIO DE ERROS E MELHORIAS)
    # --------------------------------------------------------------------------
    elif mode == "🏠 Dashboard dos Pais / Família":
        st.title(f"🏠 Acompanhamento da Família — Estudante: {st.session_state.active_student}")
        st.caption("Visão clara sobre as conquistas, acertos, erros e orientações para praticar em casa.")

        s_logs = engine.session_logs
        total_attempts = len(s_logs)
        correct_count = sum([1 for l in s_logs if l.get('correto', True)])
        error_count = total_attempts - correct_count
        acc_rate = (correct_count / total_attempts * 100.0) if total_attempts > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Exercícios Executados", total_attempts)
        m2.metric("Acertos Totais", correct_count)
        m3.metric("Erros / Hesitações", error_count)
        m4.metric("Taxa de Precisão", f"{acc_rate:.1f}%")

        st.markdown("---")
        st.subheader("📌 O que o Aluno Precisa Melhorar (Análise Automática)")

        # Tabela Detalhada de Acertos e Erros
        if s_logs:
            df_logs = pd.DataFrame(s_logs)
            st.dataframe(df_logs[['subfase', 'item', 'correto', 'precisao', 'tempo_resposta', 'dicas_usadas']], use_container_width=True)

            # Identificação de Erros
            errors_df = df_logs[df_logs['correto'] == False]
            if not errors_df.empty:
                st.warning("⚠️ **Itens em que o aluno apresentou hesitação ou erro:**")
                for idx, row in errors_df.iterrows():
                    st.write(f"- **Subfase**: {row['subfase']} | **Palavra/Item**: {row['item']} | **Tempo**: {row['tempo_resposta']}s")
            else:
                st.success("🎉 O aluno acertou todos os exercícios realizados até agora sem erros!")

        # Relatório de Orientação para a Família
        proj = engine.get_literacy_stage_and_projection()
        st.markdown(f"""
        <div style="background-color:#EAFAF1; padding:20px; border-radius:15px; border:2px solid #2ECC71;">
            <h3>🏡 Relatório de Orientação para a Família:</h3>
            <p><b>• Estágio Atual de Alfabetização:</b> {proj['stage_title']}</p>
            <p><b>• Próxima Meta:</b> {proj['next_stage']}</p>
            <p><b>• Tempo Estimado Próximo Nível:</b> ~{proj['est_minutes_left']} minutos ({proj['sessions_left']} sessões curtas de 15 min)</p>
            <p><b>• Dica de Acompanhamento em Casa:</b> {proj['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 Painel Visual de Desempenho (PNG)")
        png_s = AnalyticsDashboardGenerator.generate_student_dashboard(s_logs, engine, student_name=st.session_state.active_student)
        if png_s and os.path.exists(png_s):
            st.image(png_s, caption=f"Dashboard da Família - {st.session_state.active_student}", use_column_width=True)

    # --------------------------------------------------------------------------
    # MODO 3: PORTAL DO PROFESSOR (ACESSO RESTRITO - `prof123`)
    # --------------------------------------------------------------------------
    elif mode == "👨‍🏫 Portal do Professor (Acesso Restrito)":
        st.title("👨‍🏫 Portal do Professor — Diagnóstico Pedagógico da Turma")
        pwd_in = st.text_input("Digite a Senha do Professor:", type="password")

        if auth.verify_password(pwd_in):
            st.success("🔓 Acesso Concedido ao Portal Docente!")
            st.info(f"Link da Turma para os Alunos: **{auth.student_link}**")

            st.subheader(f"📊 Diagnóstico do Aluno Selecionado: {st.session_state.active_student}")
            proj = engine.get_literacy_stage_and_projection()

            c1, c2, c3 = st.columns(3)
            c1.metric("Habilidade Estimada", f"{engine.ability_score*100:.1f}%")
            c2.metric("Risco Sensorial FCM", f"{engine.sensory_overload_risk*100:.1f}%")
            c3.metric("Eficiência do Aprendizado", f"{proj['efficiency_rate']}%")

            st.markdown("### ⚠️ Alertas de Mediação Discreta em Tempo Real:")
            if engine.alerts:
                for a in engine.alerts:
                    st.warning(f"- {a}")
            else:
                st.success("✅ Nenhum bloqueio crítico detectado para este estudante.")

            st.markdown(f"""
            <div style="background-color:#F4ECF7; padding:20px; border-radius:15px; border:2px solid #8E44AD;">
                <h3>📋 Relatório Pedagógico Diagnóstico:</h3>
                <p><b>• Estágio Diagnosticado:</b> {proj['stage_title']}</p>
                <p><b>• Diretriz de Intervenção:</b> {proj['recommendation']}</p>
                <p><b>• Recomendação TPACK:</b> Aplicar scaffolding gradual e reforço das palavras com hesitação registrada.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            png_t = AnalyticsDashboardGenerator.generate_teacher_dashboard(engine, auth, student_name=st.session_state.active_student)
            if png_t and os.path.exists(png_t):
                st.image(png_t, caption=f"Portal do Professor - {st.session_state.active_student}", use_column_width=True)
        else:
            if pwd_in:
                st.error("🔒 Senha incorreta! Digite 'prof123'.")

# ==============================================================================
# 7. MODO STANDALONE / SIMULAÇÃO DE GERAÇÃO DE ARTEFATOS
# ==============================================================================


def run_standalone_simulation():
    print("================================================================================")
    print("INICIANDO SIMULAÇÃO E GERAÇÃO DE ARTEFATOS - VERSÃO 15 (FINAL)")
    print("================================================================================")

    db = StudentDataManager()
    engine = FuzzyCognitiveEngine(student_id="ALUNO_01", student_name="João Silva")
    auth = type('TeacherAuth', (), {'verify_password': lambda self, p: p == 'prof123', 'student_link': 'https://jogo-alfabetizacao-autismo.edu.br/aluno?turma=ef01'})()

    # Simulação de rodadas pelas 12 subfases
    sim_logs = [
        ("Fase 1", "Subfase 1.1", "BOLA", True, 7.5, 0, "Consciência Fonêmica", "Português"),
        ("Fase 1", "Subfase 1.2", "MAPA", True, 6.0, 0, "Consciência Fonêmica", "Português"),
        ("Fase 1", "Subfase 1.3", "RIO", False, 18.0, 2, "Consciência Fonêmica", "Geografia"),
        ("Fase 1", "Subfase 1.3", "RIO", True, 9.0, 1, "Consciência Fonêmica", "Geografia"),
        ("Fase 2", "Subfase 2.1", "MAPA", True, 10.0, 0, "Síntese Silábica", "Português"),
        ("Fase 2", "Subfase 2.2", "CASA", False, 15.0, 1, "Síntese Silábica", "Português"),
        ("Fase 2", "Subfase 2.3", "CADERNO", True, 12.0, 0, "Síntese Silábica", "Português"),
        ("Fase 3", "Subfase 3.1", "O RIO É BONITO", True, 11.0, 0, "Leitura Frasal", "Geografia"),
    ]

    for f, sf, it, corr, t_r, h, cat, mat in sim_logs:
        log_e = engine.process_interaction(f, sf, it, corr, t_r, h, cat, mat)
        db.add_log("João Silva", log_e)

    # Geração dos artefatos junto ao projeto para execução local e exportação.
    artifact_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(artifact_dir, exist_ok=True)
    out_s = os.path.join(artifact_dir, "dashboard-progresso-autismo-v15.png")
    out_t = os.path.join(artifact_dir, "dashboard-professor-autismo-v15.png")

    AnalyticsDashboardGenerator.generate_student_dashboard(engine.session_logs, engine, student_name="João Silva", output_path=out_s)
    AnalyticsDashboardGenerator.generate_teacher_dashboard(engine, auth, student_name="João Silva", output_path=out_t)

    shutil.copy(__file__, os.path.join(artifact_dir, os.path.basename(__file__)))

    print(f"Artefato Aluno publicado em: {out_s}")
    print(f"Artefato Professor publicado em: {out_t}")
    print(f"Código v15 publicado em: {os.path.join(artifact_dir, os.path.basename(__file__))}")

if __name__ == "__main__":
    if is_streamlit_running():
        run_streamlit_app()
    else:
        run_standalone_simulation()
