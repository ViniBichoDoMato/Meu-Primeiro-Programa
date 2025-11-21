import customtkinter as ctk
from tkcalendar import DateEntry
import sqlite3
import json
import os
from datetime import date
import tkinter as tk
from tkinter import font
from tkinter import messagebox











CONFIG_FILE = "config.json"

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"tema": "light"}

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = carregar_config()
ctk.set_appearance_mode(config["tema"])
ctk.set_default_color_theme("blue")

# === BANCO DE DADOS ===
conn = sqlite3.connect("vacinacao.db")
cursor = conn.cursor()

# Pacientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL COLLATE NOCASE,
    cpf TEXT UNIQUE,
    data_nascimento TEXT,
    unidade TEXT,
    card_sus TEXT
)
""")

# Vacinas
cursor.execute("""
CREATE TABLE IF NOT EXISTS vacinas (
    vacina_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_vacina TEXT UNIQUE,
    doses_totais TEXT
)
""")

# Paciente e vacinas (agora com CPF)
cursor.execute("""
CREATE TABLE IF NOT EXISTS paciente_vacinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    vacina_id INTEGER,
    cpf TEXT,
    dose TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
    FOREIGN KEY (vacina_id) REFERENCES vacinas(vacina_id)
)
""")

cursor.execute("""
    UPDATE paciente_vacinas
    SET dose = REPLACE(dose, 'D', '')
""")








conn.execute("PRAGMA foreign_keys = ON")



# === INTERFACE ===
app = ctk.CTk()
app.geometry("650x800")
app.title("Índice de Vacinação em Crianças(beta)")



# === ABAS ===
abas = ctk.CTkTabview(app)
abas.pack(fill="both", expand=True, padx=20, pady=20)


aba1 = abas.add("Cadastrar Paciente")
aba2 = abas.add("Pesquisar Paciente")
aba3 = abas.add("Estatísticas")
aba4 = abas.add("Configurações")

# ======================================================
# ABA 1 - CADASTRAR PACIENTE 
# ======================================================


# FRAME HORIZONTAL PRINCIPAL
frame_linha = ctk.CTkFrame(aba1)
frame_linha.pack(fill="both", pady=10, expand=True)

# Permitir expansão das colunas
frame_linha.grid_columnconfigure(0, weight=1)
frame_linha.grid_columnconfigure(1, weight=1)
frame_linha.grid_rowconfigure(0, weight=1)

# Coluna da esquerda
col_esq = ctk.CTkScrollableFrame(frame_linha, width=400, height=600)
col_esq.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

# Coluna da direita
col_dir = ctk.CTkFrame(frame_linha, width=500, height=500)
col_dir.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)


# Nome
ctk.CTkLabel(col_esq, text="Nome do Paciente:", anchor="w").pack(pady=(8,2))
campo_nome = ctk.CTkEntry(col_esq, placeholder_text="Digite o nome do paciente", width=200)
campo_nome.pack(pady=(0,10))

# CPF
ctk.CTkLabel(col_esq, text="CPF do Paciente:", anchor="w").pack(pady=(8,2))
campo_cpf = ctk.CTkEntry(col_esq, placeholder_text="Digite o CPF do paciente", width=200)
campo_cpf.pack(pady=(0,10))

# cartão SUS
ctk.CTkLabel(col_esq, text="Cartão SUS do Paciente:", anchor="w").pack(pady=(8,2))
cartao_sus = ctk.CTkEntry(col_esq, placeholder_text="Digite o Cartão SUS do paciente", width=200)
cartao_sus.pack(pady=(0,10))

# Unidade
ctk.CTkLabel(col_esq, text="Unidade do Paciente:", anchor="w").pack(pady=(8,2))
campo_unidade = ctk.CTkOptionMenu(col_esq, values=["Sem Dado" ,"17 De Abril", "Abaete", "Gravata", "KM 02", "Leste", "Oeste", "Tancredo Neves", "Viveiro"],
    width=200, fg_color="#e2ffdf", button_color="#d4f5d0", text_color="black")
campo_unidade.pack(pady=(0,10))

# Data de nascimento
def formatar_data(event, widget):
    texto = widget.get().replace("/", "")
    if not texto.isdigit():
        widget.delete(0, "end")
        widget.insert(0, "".join([c for c in texto if c.isdigit()]))
        return

    if len(texto) > 2 and texto[2] != "/":
        texto = texto[:2] + "/" + texto[2:]
    if len(texto) > 5 and texto[5] != "/":
        texto = texto[:5] + "/" + texto[5:]
    
    texto = texto[:10]  
    
    widget.delete(0, "end")
    widget.insert(0, texto)

ctk.CTkLabel(col_esq, text="Data de nascimento:", anchor="w").pack()
cal = DateEntry(col_esq, date_pattern='dd/MM/yyyy', showweeknumbers=False, background="gray", foreground="white", borderwidth=2)
cal.pack(pady=8)

cal.bind("<KeyRelease>", lambda e: formatar_data(e, cal))

# Frame para lista de pacientes encontrados
frame_lista_pacientes = ctk.CTkFrame(col_dir, fg_color="#e3e3e3", border_width=1, border_color="black", width=100, height=100)
frame_lista_pacientes.pack(fill="both", expand=True, padx=10, pady=10)

texto_lista = ctk.CTkTextbox(frame_lista_pacientes, width=350, height=250)
texto_lista.pack(fill="both", expand=True, padx=10, pady=10)
    
# Vacinas
ctk.CTkLabel(col_esq, text="Quantas Doses Aplicada:", anchor="w").pack(pady=(10,6))

nomes_vacinas = ["VIP", "Pentavalente", "Hexavalente", "Pneumocócica", "Hepatite B", "BCG", "Rotavírus", "DTP", "Feble Amarela", "Meningocócica ACWY", "Hepatite A", "Varicela", "Meningocócica C (Conjugada)", "Triplice Viral", "Influenza Trivalente", "Tetra Viral", "HPV"]


# Insere vacinas na tabela se não existirem
for i, nome in enumerate(nomes_vacinas, start=1):
    cursor.execute("INSERT OR IGNORE INTO vacinas (vacina_id, nome_vacina) VALUES (?, ?)", (i, nome))







combobox_map = {}

dose_vars = []



def criar_optionmenus():
    global combobox_map   # agora o Python sabe qual é
    global dose_vars


    for nome in nomes_vacinas:
        linha = ctk.CTkFrame(col_esq)
        linha.pack(fill="x", pady=2, padx=10)

        dose_var = ctk.StringVar(value="0D")
        dose_menu = ctk.CTkOptionMenu(linha, values=["0D", "1D", "2D", "3D", "4D"],
            variable=dose_var, width=80, height=26, fg_color="#e2ffdf", button_color="#d4f5d0", text_color="black")
        dose_menu.pack(side="left", padx=(0, 10))

        vacinas_op = ctk.CTkLabel(linha, text=nome)
        vacinas_op.pack(side="left")



        dose_vars.append(dose_var)

        combobox_map[nome] = dose_var
criar_optionmenus()
# ======================================================
# FUNÇÕES
# ======================================================
def preencher_campos_do_paciente(pid):
    cursor.execute("""
        SELECT nome, cpf, data_nascimento, unidade, card_sus
        FROM pacientes
        WHERE id = ?
    """, (pid,))
    
    paciente = cursor.fetchone()

    if not paciente:
        return

    nome, cpf, data, unidade, cartao = paciente

    campo_nome.delete(0, "end")
    campo_nome.insert(0, nome)

    campo_cpf.delete(0, "end")
    campo_cpf.insert(0, cpf)

    cartao_sus.delete(0, "end")
    cartao_sus.insert(0, cartao if cartao else "")

    campo_unidade.set(unidade if unidade else "Sem Dado")
    cal.set_date(data)

    # Limpar combobox antes
    for cb in combobox_map.values():
        cb.set("")

    # Carregar vacinas do banco
    cursor.execute("""
        SELECT v.nome_vacina, pv.dose
        FROM vacinas v
        JOIN paciente_vacinas pv ON v.vacina_id = pv.vacina_id
        WHERE pv.paciente_id = ?
    """, (pid,))
    vacinas = cursor.fetchall()

    for vacina, dose in vacinas:
        combobox_map[vacina].set(f"{dose}D")





def carregar_paciente_para_edicao():
    data_nasc = cal.get().strip()

    cursor.execute("""
        SELECT id, nome, cpf, unidade, card_sus, data_nascimento
        FROM pacientes
        WHERE data_nascimento = ?
    """, (data_nasc,))
    
    pacientes = cursor.fetchall()

    # Limpar lista antiga
    for widget in frame_lista_pacientes.winfo_children():
        widget.destroy()

    # Caso 0 → nenhum paciente
    if not pacientes:
        messagebox.showinfo("Aviso", "Nenhum paciente encontrado com essa data.")
        return

    # Caso 1 → carregar direto
    if len(pacientes) == 1:
        pid = pacientes[0][0]
        preencher_campos_do_paciente(pid)
        return

    # Caso 2+ → mostrar lista para escolher
    ctk.CTkLabel(
        frame_lista_pacientes,
        text=f"Foram encontrados {len(pacientes)} pacientes.\nSelecione um:",
        font=("Arial", 14)
    ).pack(pady=5)

    # Criar botão para cada paciente
    for pid, nome, cpf, unidade, card_sus, data_nascimento in pacientes:

        texto = f"{nome} — CPF: {cpf}"

        def carregar(pid_atual=pid):
            preencher_campos_do_paciente(pid_atual)

        ctk.CTkButton(
            frame_lista_pacientes,
            text=texto,
            command=carregar,
            width=300
        ).pack(pady=4)


def limpar_campos():
    # Limpa entradas simples
    campo_nome.delete(0, "end")
    campo_cpf.delete(0, "end")
    cartao_sus.delete(0, "end")
    campo_unidade.set("Sem Dado")

    # Reseta data (coloca uma data padrão, como HOJE)
    cal.set_date(date.today())

    # zera as doses
    for dose_var in dose_vars:
        dose_var.set("0D")






def salvar_dados():
    nome = campo_nome.get().strip()
    cpf = campo_cpf.get().strip().replace(".", "").replace("-", "")
    data_nasc = cal.get()
    cartao = cartao_sus.get().strip()
    unidade = campo_unidade.get().strip()

    if not nome or not cpf:
        print("⚠️ Nome e CPF são obrigatórios!")
        return

    if len(cpf) != 11 or not cpf.isdigit():
            messagebox.showerror("Erro", "O CPF deve conter exatamente 11 números.")
            return



  # SEM checkboxes → salva TODAS as vacinas sempre
    vacinas_marcadas = []
    for nome_vacina, dose_var in zip(nomes_vacinas, dose_vars):
        dose = dose_var.get()
        vacinas_marcadas.append((nome_vacina, dose))  

    cursor.execute("SELECT id FROM pacientes WHERE cpf = ?", (cpf,))
    existente = cursor.fetchone()

    if existente:
        paciente_id = existente[0]
        cursor.execute("""UPDATE pacientes SET nome = ?, data_nascimento = ?, unidade = ?, card_sus = ?WHERE id = ?""", (nome, data_nasc, cartao, unidade, paciente_id))
        cursor.execute("DELETE FROM paciente_vacinas WHERE paciente_id = ?", (paciente_id,))
        print(f"🔄 Atualizando paciente '{nome}' ({cpf})...")
    else:
        cursor.execute("""INSERT INTO pacientes (nome, cpf, data_nascimento, unidade, card_sus)VALUES (?, ?, ?, ?, ?)""", (nome, cpf, data_nasc, cartao, unidade))
        paciente_id = cursor.lastrowid
        print(f"🆕 Novo paciente '{nome}' ({cpf}) adicionado.")

    for nome_vacina, dose_str in vacinas_marcadas:

        # pega ID da vacina
        cursor.execute("SELECT vacina_id FROM vacinas WHERE nome_vacina = ?", (nome_vacina,))
        row = cursor.fetchone()
        if not row:
            continue
        vacina_id = row[0]

        # extrai número da dose
        dose_num = int(dose_str.replace("D", "").strip())

        cursor.execute("""
            INSERT INTO paciente_vacinas (paciente_id, vacina_id, cpf, dose, unidade)
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_id, vacina_id, cpf, dose_num, unidade))
  
        

    

    conn.commit()
    
    print(f"✅ Dados de '{nome}' ({cpf}) salvos com sucesso!")
    
    atualizar_estatisticas()
    limpar_campos() 
    print("🧹 Campos limpos para novo cadastro.")

def buscar_para_edicao():
    nome = campo_nome.get().strip()
    if not nome:
        print("⚠️ Digite o nome do paciente para buscar e editar.")
        return
    carregar_paciente_para_edicao(nome)

ctk.CTkButton(col_esq, text="💾 Salvar Dados", command=salvar_dados, fg_color="#e2ffdf", text_color="black").pack(pady=10)
ctk.CTkButton(col_esq, text="✏️ Buscar Paciente para Editar", command=carregar_paciente_para_edicao, fg_color="#e2ffdf", text_color="black").pack(pady=(10, 5))

# ======================================================
# ABA 2 - PESQUISAR PACIENTE
# ======================================================
frame_linha2 = ctk.CTkFrame(aba2)
frame_linha2.pack(fill="both", pady=10, expand=True)

# Permitir expansão das colunas
frame_linha2.grid_columnconfigure(0, weight=1)
frame_linha2.grid_columnconfigure(1, weight=1)
frame_linha2.grid_rowconfigure(0, weight=1)

# Coluna da esquerda
col_esq2 = ctk.CTkFrame(frame_linha2, width=400, height=600)
col_esq2.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

# Coluna da direita
col_dir2 = ctk.CTkFrame(frame_linha2, width=500, height=500)
col_dir2.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)


ctk.CTkLabel(col_esq2, text="Pesquisar Paciente", font=("Arial", 18)).pack(pady=10)

frame_texto = ctk.CTkFrame(col_esq2, border_width=1, border_color="white", corner_radius=1)
frame_texto.pack(padx=10, pady=10)


ctk.CTkLabel(frame_texto, text="Digite a Data de Nacimento do paciente:").pack(padx=1, pady=1)

campo_data_pesq = DateEntry(col_esq2, date_pattern='dd/MM/yyyy', showweeknumbers=False, background="gray", foreground="white", borderwidth=2)
campo_data_pesq.pack(pady=10)

campo_data_pesq.bind("<KeyRelease>", lambda e: formatar_data(e, campo_data_pesq))



texto_resultado = ctk.CTkTextbox(col_esq2, height=400, width=500)
texto_resultado.pack(pady=10, padx=10)

# 🔹 Frame que aparece apenas se houver mais de 1 paciente com a mesma data
frame_escolha = ctk.CTkFrame(col_dir2)
frame_escolha.pack(pady=5)
frame_escolha.pack_forget()  # Inicialmente invisível

lista_pacientes_btns = []  # para apagar depois


def exibir_paciente(paciente_id):
    """Carrega o paciente selecionado e oculta os botões."""
    texto_resultado.delete("1.0", "end")

    cursor.execute("""
            SELECT nome, cpf, data_nascimento, unidade, card_sus 
            FROM pacientes 
            WHERE id = ?
        """, (paciente_id,))
    
    paciente = cursor.fetchone()
    nome, cpf, data_nasc, unidade, cartao = paciente

    cursor.execute("""
        SELECT v.nome_vacina, pv.dose
        FROM vacinas v
        JOIN paciente_vacinas pv ON v.vacina_id = pv.vacina_id
        WHERE pv.paciente_id = ?
    """, (paciente_id,))
    vacinas_lista = cursor.fetchall()

    # Ocultar botões
    for b in lista_pacientes_btns:
        b.destroy()
    frame_escolha.pack_forget()

    # Mostrar resultado formatado
    resultado = (
        f"📋 Nome: {nome}\n"
        f"🪪 CPF: {cpf}\n"
        f"💳 Cartão SUS: {cartao if cartao else 'Sem dado'}\n"
        f"🏥 Unidade: {unidade if unidade else 'Sem dado'}\n"
        f"🎂 Data de nascimento: {data_nasc}\n\n"
        f"💉 Vacinas aplicadas:\n"
    )

    if vacinas_lista:
        for vacina, dose in vacinas_lista:
            resultado += f"  - {vacina} ({dose})\n"
    else:
        resultado += "  (Nenhuma vacina registrada)\n"

    texto_resultado.insert("1.0", resultado)




def pesquisar_paciente():
    data = campo_data_pesq.get().strip()
    texto_resultado.delete("1.0", "end")

    for b in lista_pacientes_btns:
        b.destroy()
    lista_pacientes_btns.clear()
    frame_escolha.pack_forget()



    if not data:
        texto_resultado.insert("1.0", "⚠️ Digite uma data.")
        return

    cursor.execute("""SELECT id, nome, cpf FROM pacientes WHERE data_nascimento = ?""", (data,))
    lista = cursor.fetchall()
    
    if not lista:
        texto_resultado.insert("1.0", f"❌ Nenhum paciente encontrado para {data}.")
        return
    
    # 🔹 Se só existe um paciente → mostra direto
    if len(lista) == 1:
        exibir_paciente(lista[0][0])
        return
    
    # 🔹 Se existem vários → criar botões para escolha
    texto_resultado.insert("1.0", f"📌 Foram encontrados {len(lista)} pacientes.\nSelecione um:")

    frame_escolha.pack(pady=5)

    for pid, nome, cpf in lista:
        btn = ctk.CTkButton(frame_escolha, text=f"{nome}  |  CPF: {cpf}",
                            command=lambda p=pid: exibir_paciente(p))
        btn.pack(pady=2, fill="x")
        lista_pacientes_btns.append(btn)



ctk.CTkButton(col_esq2, text="🔍 Pesquisar", command=pesquisar_paciente).pack(pady=10)

campo_data_pesq.bind("<Return>", lambda e: pesquisar_paciente())
aba2.bind("<Return>", lambda e: pesquisar_paciente())
# ======================================================
# ABA 3 - Estatisticas
# ======================================================
scroll_estatisticas = ctk.CTkScrollableFrame(master=aba3)
scroll_estatisticas.pack(fill="both", expand=True, padx=0, pady=10)

def estatisticas_completas():
    conn = sqlite3.connect("vacinacao.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
    p.id AS paciente_id,
    v.vacina_id,
    v.nome_vacina,
    v.doses_totais,
    COALESCE(SUM(pv.dose), 0) AS doses_aplicadas
    FROM pacientes p
    CROSS JOIN vacinas v
    LEFT JOIN paciente_vacinas pv 
    ON pv.paciente_id = p.id
    AND pv.vacina_id = v.vacina_id
    GROUP BY p.id, v.vacina_id;
    """)

    dados = cursor.fetchall()
    return dados






dados = estatisticas_completas()

# doses aplicadas por vacina
doses_aplicadas_por_vacina = {}
# doses faltando por vacina
doses_faltando_por_vacina = {}
# total de doses aplicadas no sistema
doses_totais_aplicadas = 0
# pacientes que nunca tomaram nenhuma dose
pacientes_sem_doses = set()

doses_totais_por_vacina = {}
for pac_id, vac_id, nome, doses_totais, aplicadas in dados:

    doses_totais_por_vacina[vac_id] = doses_totais

    doses_totais_aplicadas += aplicadas

    # registra vacina no dicionário se ainda não existir
    if vac_id not in doses_aplicadas_por_vacina:
        doses_aplicadas_por_vacina[vac_id] = 0
        doses_faltando_por_vacina[vac_id] = 0

    # soma doses aplicadas
    doses_aplicadas_por_vacina[vac_id] += aplicadas

    # calcula faltando
    faltando = max(doses_totais - aplicadas, 0)
    doses_faltando_por_vacina[vac_id] += faltando

    # marca pacientes que não tomaram nada
    if aplicadas == 0:
        pacientes_sem_doses.add(pac_id)






# Quantidade de pacientes
def somar_pacientes():
    conn = sqlite3.connect("vacinacao.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM pacientes")
    total = cursor.fetchone()[0]

    conn.close()
    return total

def atualizar_estatisticas():
    total = somar_pacientes()
    total_de_pacientes.configure(text=f"Quantidade de Pacientes Cadastrados: {total}")


total_de_pacientes = ctk.CTkLabel(scroll_estatisticas, text="Quantidade de Pacientes Cadastrados", font=("Arial", 17))
total_de_pacientes.pack(anchor="w", pady=10)

atualizar_estatisticas() 

# Vacinas aplicadas por dose para cada vacina


vacinas = ctk.CTkLabel(scroll_estatisticas, text="Vacinas", font=("Arial", 17))
vacinas.pack(anchor="w", pady=17)

# --- CRIA DUAS COLUNAS ---
# Frame central que segura as duas colunas
container = ctk.CTkFrame(scroll_estatisticas, fg_color="transparent")
container.pack(fill="both", expand=False, padx=0, pady=0)

# Coluna da esquerda
col_esq = ctk.CTkFrame(container, fg_color="#e2ffdf", width=200, corner_radius=8)
col_esq.grid(row=0, column=0, sticky="nw", padx=(0,10), pady=0)

# Espaço fixo no meio (controle do alinhamento)
col_vazio = ctk.CTkFrame(container, fg_color="transparent", width=40)
col_vazio.grid(row=0, column=1)

# Coluna da direita
col_dir = ctk.CTkFrame(container, fg_color="#e2ffdf", width=200, corner_radius=8)
col_dir.grid(row=0, column=2, sticky="ne", padx=(0,0), pady=0)



vacinas = ["VIP", "Pentavalente", "Hexavalente", "Pneumocócica", "Hepatite B", "BCG", "Rotavírus", "DTP", "Feble Amarela", "Meningocócica ACWY", "Hepatite A", "Varicela", "Meningocócica C (Conjugada)", "Triplice Viral", "Influenza Trivalente", "Tetra Viral", "HPV"]


total_pacientes = somar_pacientes() 


# quatidade de vacinas↑
def contar_vacinas():
    conn = sqlite3.connect("vacinacao.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vacina_id,
               SUM(
                   CASE
                       WHEN TRIM(REPLACE(dose, 'D', '')) = '' THEN 0
                       ELSE CAST(TRIM(REPLACE(dose, 'D', '')) AS INTEGER)
                   END
               ) AS total_doses
        FROM paciente_vacinas
        GROUP BY vacina_id
    """)
    
    dados = cursor.fetchall()
    conn.close()
    return {vac_id: (total if total is not None else 0) for vac_id, total in dados}
    
totais = contar_vacinas()
total_pacientes = somar_pacientes()

totais_doses = contar_vacinas()  

def contar_pacientes_por_vacina():
    conn = sqlite3.connect("vacinacao.db")
    cursor = conn.cursor()

    # Conta quantos pacientes tomaram pelo menos 1 dose de cada vacina
    cursor.execute("""
        SELECT vacina_id, COUNT(DISTINCT paciente_id) as qtd_pacientes
        FROM paciente_vacinas
        WHERE CAST(TRIM(REPLACE(dose,'D','')) AS INTEGER) > 0
        GROUP BY vacina_id
    """)
    dados = cursor.fetchall()
    return {vac_id: qtd for vac_id, qtd in dados}




    




totais_pacientes_vac = contar_pacientes_por_vacina()   
totais_doses = contar_vacinas()
totais_pacientes_vac = contar_pacientes_por_vacina()
total_pacientes = somar_pacientes()



# LISTA DA ESQUERDA (vacina + porcentagem à direita)
for index, nome in enumerate(vacinas, start=1):  # index == vacina_id
    
    doses_aplicadas = doses_aplicadas_por_vacina.get(index, 0)
    doses_necessarias = total_pacientes * doses_totais_por_vacina.get(index, 0)
    
    porcentagem_doses = (doses_aplicadas / doses_necessarias * 100 if doses_necessarias > 0 else 0)

    ctk.CTkLabel(col_esq, text=f"{nome}: {porcentagem_doses:.1f}%",anchor="w").pack(fill="x", padx=8, pady=6)
        

# LISTA DA DIREITA (número + ":" + vacina, tudo alinhado à direita)
for index, nome in enumerate(vacinas, start=1):
    total = doses_aplicadas_por_vacina.get(index, 0)

    ctk.CTkLabel(col_dir, text=f"{nome}: {total}", anchor="w").pack(fill="x", padx=8, pady=6)



# doses faltando de cada vacina



ctk.CTkLabel(scroll_estatisticas ,text="Doses em falta", font=("Arial", 17) ).pack(pady=10, anchor="w")

frame_doses_faltando = ctk.CTkFrame(scroll_estatisticas, fg_color="#e2ffdf", corner_radius=10, height=200)
frame_doses_faltando.pack(pady=10, fill="x", expand=True)

colunas = 5

for i, item in enumerate(vacinas):
    coluna = i % colunas
    linha = i // colunas
    

    frame_doses_faltando.grid_columnconfigure(coluna, weight=1)

    vacina_id = i + 1 

    doses_aplicadas = totais_doses.get(vacina_id, 0)


# Cálculo das doses faltando
    doses_faltando = doses_faltando_por_vacina.get(vacina_id, 0)

# cálculo em porcentagem
    doses_necessarias = total_pacientes * doses_totais_por_vacina.get(vacina_id, 0)

    if doses_necessarias > 0:
        porc_faltando = doses_faltando / doses_necessarias * 100
    else:
        porc_faltando = 0.0



# frame com nome das vacinas, quantidade e porcentagem de doses faltando
    ctk.CTkLabel(frame_doses_faltando, text=item).grid(row=linha*3, column=coluna, padx=20, pady=(10, 2))

    ctk.CTkLabel(frame_doses_faltando, text=str(doses_faltando)).grid(row=linha*3 + 1, column=coluna, padx=20, pady=(2, 2))

    ctk.CTkLabel(frame_doses_faltando, text=f"{porc_faltando:.1f}%").grid(row=linha*3 + 2, column=coluna, padx=20, pady=(2, 10))

# soma de todas as doses aplicadas (numericamente e percentualmente)

ctk.CTkLabel(scroll_estatisticas ,text="Total de doses aplicadas", font=("Arial", 17) ).pack(pady=10, anchor="w")

frame_total = ctk.CTkFrame(scroll_estatisticas, fg_color="#e2ffdf")
frame_total.pack(pady=10, expand=True, anchor="w")

def doses_totas():
    conn = sqlite3.connect("vacinacao.db")
    cursor = conn.cursor()

    cursor.execute("""SELECT SUM(dose) FROM paciente_vacinas;""")
    resultado = cursor.fetchone()
    conn.close()

    total_doses = resultado[0] if resultado[0] is not None else 0
    return total_doses

total = doses_totais_aplicadas

ctk.CTkLabel(frame_total, text=f"Doses aplicadas: {total}", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=(2, 10))


def doses_numero():
    cursor.execute("SELECT SUM(dose) FROM paciente_vacinas;")
    resultado = cursor.fetchone()[0]
    return resultado if resultado is not None else 0
conn.commit()







# ======================================================
# ABA 4 - CONFIGURAÇÕES
# ======================================================
ctk.CTkLabel(aba4, text="Tema da Interface", font=("Arial", 16)).pack(pady=20)
def alternar_tema():
    modo_atual = ctk.get_appearance_mode().lower()
    novo = "light" if modo_atual == "dark" else "dark"
    ctk.set_appearance_mode(novo)
    atualizar_borda_frame()
    salvar_config({"tema": novo})
    print(f"Tema alterado para: {novo}")

ctk.CTkButton(aba4, text="Alternar Tema", command=alternar_tema).pack(pady=10)

# --- frame com borda dinâmica ---
def atualizar_borda_frame():
    tema = ctk.get_appearance_mode()
    cor_borda = "white" if tema == "Dark" else "black"
    frame_texto.configure(border_color=cor_borda)

# Run
app.mainloop()
conn.commit()
conn.close()



