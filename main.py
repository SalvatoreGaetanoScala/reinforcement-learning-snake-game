import pygame
import numpy as np
import random
import sys
import os
import subprocess
import multiprocessing as mp
from stable_baselines3 import PPO
from snake_env import SnakeEnv

from ui import (
    disegna_menu_iniziale, 
    disegna_pannello_ui_addestramento, 
    disegna_grafici_dashboard, 
    disegna_game_over_classico,
    disegna_popup_info,
    ROSSO_PULSANTE
)

BLOCCO = 20

def porta_finestra_in_primo_piano():
    if sys.platform == "darwin":
        try:
            script = (
                'tell application "System Events" to set frontmost of '
                'first process whose unix id is {} to true'.format(os.getpid())
            )
            subprocess.run(["osascript", "-e", script], check=False,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def finestra_parametri_process(queue):
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Monitoraggio Algoritmo RL")
    root.geometry("380x420")
    root.configure(bg="#2d2d2d")
    
    tk.Label(root, text="Dati e Parametri PPO", font=("Arial", 14, "bold"), bg="#2d2d2d", fg="#4CAF50").pack(pady=10)
    
    labels = {}
    parametri = {
        "Algoritmo": "PPO (Stable-Baselines3)",
        "Learning Rate": "3e-4 (Lineare)",
        "Gamma (Discount)": "0.999",
        "Entropy Coef": "0.01",
        "Architettura Rete": "pi: [256, 256], vf: [256, 256]",
        "N-Steps": "2048",
        "Batch Size": "64",
        "Epoche": "10",
        "---": "---",
        "Episodi Totali": "0",
        "Step Totali Ambienti": "0",
        "Premio RL (Episodio Corrente)": "0.000"
    }
    
    for k, v in parametri.items():
        frame = tk.Frame(root, bg="#2d2d2d")
        frame.pack(fill="x", padx=15, pady=3)
        
        if k == "---":
            tk.Frame(root, height=2, bg="#555555").pack(fill="x", pady=5, padx=10)
            continue
        
        tk.Label(frame, text=f"{k}:", font=("Arial", 10, "bold"), bg="#2d2d2d", fg="#87CEEB").pack(side="left")
        lbl_v = tk.Label(frame, text=v, font=("Arial", 10), bg="#2d2d2d", fg="white")
        lbl_v.pack(side="right")
        labels[k] = lbl_v

    def aggiorna():
        try:
            while not queue.empty():
                msg = queue.get_nowait()
                if msg == "QUIT":
                    root.destroy()
                    return
                else:
                    episodi, passi, premio = msg
                    labels["Episodi Totali"].config(text=str(episodi))
                    labels["Step Totali Ambienti"].config(text=str(passi))
                    labels["Premio RL (Episodio Corrente)"].config(text=f"{premio:.3f}")
        except Exception:
            pass
        root.after(50, aggiorna)

    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.after(50, aggiorna)
    root.mainloop()

# --- FUNZIONI DI GIOCO ---
def genera_mela(max_grid_x, max_grid_y, min_grid_y, lista_snake):
    while True:
        mx = max(0, max_grid_x)
        my = max(min_grid_y, max_grid_y)
        m_x = random.randint(0, mx) * BLOCCO
        m_y = random.randint(min_grid_y, my) * BLOCCO
        if [m_x, m_y] not in lista_snake:
            return m_x, m_y

def calcola_stato(testa_x, testa_y, x_cambio, y_cambio, mela_x, mela_y, lista_snake, larghezza, altezza, min_y):
    stato = []
    direzioni = [
        (0, -BLOCCO), (0, BLOCCO), (-BLOCCO, 0), (BLOCCO, 0),
        (-BLOCCO, -BLOCCO), (BLOCCO, -BLOCCO), (-BLOCCO, BLOCCO), (BLOCCO, BLOCCO)
    ]
    
    for dx, dy in direzioni:
        dist_muro = 0.0
        dist_mela = 0.0
        dist_corpo = 0.0
        
        x, y = testa_x, testa_y
        step = 1
        
        while True:
            x += dx
            y += dy
            
            if x < 0 or x >= larghezza or y < min_y or y >= altezza:
                dist_muro = 1.0 / step
                break
                
            if dist_corpo == 0.0 and [x, y] in lista_snake[:-1]:
                dist_corpo = 1.0 / step
                
            if dist_mela == 0.0 and x == mela_x and y == mela_y:
                dist_mela = 1.0 / step
                
            step += 1
            
        stato.extend([dist_muro, dist_mela, dist_corpo])
        
    dir_u = int(y_cambio == -BLOCCO)
    dir_d = int(y_cambio == BLOCCO)
    dir_l = int(x_cambio == -BLOCCO)
    dir_r = int(x_cambio == BLOCCO)
    if x_cambio == 0 and y_cambio == 0: dir_r = 1 
    
    stato.extend([dir_u, dir_l, dir_d, dir_r])
    return np.array(stato, dtype=np.float32)

def menu_iniziale():
    global dis, clock
    while True:
        w, h = dis.get_width(), dis.get_height()
        btn_classico, btn_addestramento = disegna_menu_iniziale(dis, w, h)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                dis = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_classico.collidepoint(event.pos): return "classico"
                if btn_addestramento.collidepoint(event.pos): return "addestramento"
        clock.tick(15)

def loop_classico():
    global dis, clock
    w, h = dis.get_width(), dis.get_height()
    x1 = w // 2 // BLOCCO * BLOCCO
    y1 = h // 2 // BLOCCO * BLOCCO
    x1_cambio, y1_cambio = 0, 0
    lista_snake = [[x1, y1]]
    lunghezza = 1
    
    mela_x, mela_y = genera_mela(w//BLOCCO-1, h//BLOCCO-1, 0, lista_snake)
    game_over = False
    running = True
    ultimo_aggiornamento = pygame.time.get_ticks()
    
    btn_rip, btn_men, btn_esc = None, None, None
    
    while running:
        w, h = dis.get_width(), dis.get_height()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                dis = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                w, h = event.w, event.h
                if mela_x >= w or mela_y >= h:
                    mela_x, mela_y = genera_mela(w//BLOCCO-1, h//BLOCCO-1, 0, lista_snake)
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    if btn_rip and btn_rip.collidepoint(event.pos): return "classico" 
                    if btn_men and btn_men.collidepoint(event.pos): return "MENU"     
                    if btn_esc and btn_esc.collidepoint(event.pos): return "QUIT"     
            
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_w and y1_cambio != BLOCCO: x1_cambio, y1_cambio = 0, -BLOCCO
                elif event.key == pygame.K_a and x1_cambio != BLOCCO: x1_cambio, y1_cambio = -BLOCCO, 0
                elif event.key == pygame.K_s and y1_cambio != -BLOCCO: x1_cambio, y1_cambio = 0, BLOCCO
                elif event.key == pygame.K_d and x1_cambio != -BLOCCO: x1_cambio, y1_cambio = BLOCCO, 0

        ora = pygame.time.get_ticks()
        if not game_over and (ora - ultimo_aggiornamento) >= 80:
            ultimo_aggiornamento = ora
            if x1_cambio != 0 or y1_cambio != 0:
                x1 += x1_cambio
                y1 += y1_cambio
                
                mangia_ora = (x1 == mela_x and y1 == mela_y)
                corpo_da_controllare = lista_snake if mangia_ora else lista_snake[:-1]
                if x1 < 0 or x1 >= w or y1 < 0 or y1 >= h or [x1, y1] in corpo_da_controllare:
                    game_over = True
                else:
                    lista_snake.insert(0, [x1, y1])
                    if len(lista_snake) > lunghezza: del lista_snake[-1]
                    if x1 == mela_x and y1 == mela_y:
                        lunghezza += 1
                        mela_x, mela_y = genera_mela(w//BLOCCO-1, h//BLOCCO-1, 0, lista_snake)
                        
        dis.fill((0, 0, 0))
        if game_over:
            btn_rip, btn_men, btn_esc = disegna_game_over_classico(dis, w, h)
        else:
            btn_rip, btn_men, btn_esc = None, None, None
            pygame.draw.rect(dis, ROSSO_PULSANTE, [mela_x, mela_y, BLOCCO, BLOCCO])
            for p in lista_snake:
                pygame.draw.rect(dis, (0, 255, 0), [p[0], p[1], BLOCCO, BLOCCO])
                
        pygame.display.update()
        clock.tick(60)

def loop_addestramento():
    global dis, clock, env, model, modello_caricato
    slider_val = 0.0
    dragging_slider = False
    mostra_popup = False
    btn_chiudi = None
    
    h_ui = 120
    h_grafici = 160
    
    w_tot = dis.get_width()
    h_tot = dis.get_height()
    w_game = w_tot
    h_game = h_tot - h_grafici
    
    x1 = w_game // 2 // BLOCCO * BLOCCO
    y1 = max(h_ui, h_game // 2 // BLOCCO * BLOCCO)
    x1_cambio, y1_cambio = BLOCCO, 0
    lista_snake = [[x1, y1], [x1-20, y1], [x1-40, y1]]
    lunghezza = 3
    
    mela_x, mela_y = genera_mela(w_game//BLOCCO-1, h_game//BLOCCO-1, h_ui//BLOCCO, lista_snake)
    
    running = True
    ultimo_aggiornamento = pygame.time.get_ticks()
    track_rect, area_slider, btn_info = None, None, None

    # Avvio la finestra Tkinter isolata
    queue = mp.Queue()
    tk_process = mp.Process(target=finestra_parametri_process, args=(queue,))
    tk_process.start()
    porta_finestra_in_primo_piano()
    
    premio_reale_ep = 0.0

    while running:
        w_tot, h_tot = dis.get_width(), dis.get_height()
        w_game = w_tot
        h_game = h_tot - h_grafici
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.salva_statistiche()
                queue.put("QUIT")
                tk_process.join(timeout=1)
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                dis = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                w_game = event.w
                h_game = event.h - h_grafici
                if mela_x >= w_game or mela_y >= h_game:
                    mela_x, mela_y = genera_mela(w_game//BLOCCO-1, h_game//BLOCCO-1, h_ui//BLOCCO, lista_snake)
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mostra_popup:
                    # Se clicco il tasto chiudi nel popup
                    if btn_chiudi and btn_chiudi.collidepoint(event.pos):
                        mostra_popup = False
                else:
                    if area_slider and area_slider.collidepoint(event.pos):
                        dragging_slider = True
                    elif btn_info and btn_info.collidepoint(event.pos):
                        mostra_popup = True
                        
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider and track_rect:
                    sx = track_rect.x
                    sw = track_rect.width
                    rel_x = max(0, min(event.pos[0] - sx, sw))
                    slider_val = (rel_x / sw) * 2.0 - 1.0

        # Se il popup è aperto, mette in pausa il gioco disegnando solo l'interfaccia
        if mostra_popup:
            btn_chiudi = disegna_popup_info(dis, w_tot, h_tot)
            pygame.display.update()
            clock.tick(15)
            continue

        ora = pygame.time.get_ticks()
        
        base_delay = 66
        if slider_val == 1.0:
            ritardo, passi = 0, 50
        elif slider_val >= 0:
            ritardo, passi = int(base_delay * (1.0 - slider_val)), 1
        else:
            ritardo, passi = int(base_delay + (abs(slider_val) * 250)), 1

        for _ in range(passi):
            if (ora - ultimo_aggiornamento) >= ritardo:
                ultimo_aggiornamento = ora
                env.passi_totali += 1 

                distanza_prima = np.linalg.norm(np.array([x1, y1]) - np.array([mela_x, mela_y]))

                if modello_caricato:
                    obs = calcola_stato(x1, y1, x1_cambio, y1_cambio, mela_x, mela_y, lista_snake, w_game, h_game, h_ui)
                    azione, _ = model.predict(obs)
                    
                    if azione == 0 and y1_cambio != BLOCCO: x1_cambio, y1_cambio = 0, -BLOCCO
                    elif azione == 1 and x1_cambio != BLOCCO: x1_cambio, y1_cambio = -BLOCCO, 0
                    elif azione == 2 and y1_cambio != -BLOCCO: x1_cambio, y1_cambio = 0, BLOCCO
                    elif azione == 3 and x1_cambio != -BLOCCO: x1_cambio, y1_cambio = BLOCCO, 0

                x1 += x1_cambio
                y1 += y1_cambio
                
                distanza_dopo = np.linalg.norm(np.array([x1, y1]) - np.array([mela_x, mela_y]))
                
                mangia_ora = (x1 == mela_x and y1 == mela_y)
                corpo_da_controllare = lista_snake if mangia_ora else lista_snake[:-1]
                hit_wall = x1 < 0 or x1 >= w_game or y1 < h_ui or y1 >= h_game
                hit_self = [x1, y1] in corpo_da_controllare
                starved = env.frame_iteration > 100 * lunghezza
                
                morto = hit_wall or hit_self or starved

                reward_step = 0.0

                if morto:
                    if hit_self: 
                        env.premio -= 100
                        reward_step = -2.0
                    elif hit_wall: 
                        env.premio -= 50
                        reward_step = -1.5
                    else:
                        env.premio -= 10
                        reward_step = -1.0
                    
                    premio_reale_ep += reward_step
                    
                    env.iterazioni += 1
                    
                    mele_mangiate = lunghezza - 3
                    env.storico_mele.append(mele_mangiate)
                    env.storico_passi.append(env.frame_iteration)
                    
                    if mele_mangiate > env.record_mele: env.record_mele = mele_mangiate
                    if env.frame_iteration > env.record_passi: env.record_passi = env.frame_iteration

                    env.storico_mele = env.storico_mele[-100:]
                    env.storico_passi = env.storico_passi[-100:]
                    
                    env.salva_statistiche()
                    
                    x1 = w_game // 2 // BLOCCO * BLOCCO
                    y1 = max(h_ui, h_game // 2 // BLOCCO * BLOCCO)
                    x1_cambio, y1_cambio = BLOCCO, 0
                    lista_snake = [[x1, y1], [x1-20, y1], [x1-40, y1]]
                    lunghezza = 3
                    env.frame_iteration = 0
                    premio_reale_ep = 0.0
                else:
                    lista_snake.insert(0, [x1, y1])
                    if len(lista_snake) > lunghezza: del lista_snake[-1]
                    
                    if mangia_ora:
                        env.premio += 10
                        reward_step = 10.0
                        env.salva_statistiche()
                        lunghezza += 1
                        mela_x, mela_y = genera_mela(w_game//BLOCCO-1, h_game//BLOCCO-1, h_ui//BLOCCO, lista_snake)
                    else:
                        if distanza_dopo < distanza_prima:
                            reward_step = 0.015
                        else:
                            reward_step = -0.015
                        reward_step -= 0.005
                        
                    premio_reale_ep += reward_step
                    env.frame_iteration += 1

        # Aggiornamento fluido via Queue
        try:
            queue.put_nowait((env.iterazioni, env.passi_totali, premio_reale_ep))
        except:
            pass

        dis.fill((0, 0, 0))
        pygame.draw.rect(dis, ROSSO_PULSANTE, [mela_x, mela_y, BLOCCO, BLOCCO])
        for p in lista_snake:
            pygame.draw.rect(dis, (0, 255, 0), [p[0], p[1], BLOCCO, BLOCCO])
            
        mele_attuali = lunghezza - 3
        
        track_rect, area_slider, btn_info = disegna_pannello_ui_addestramento(
            dis, premio_reale_ep, mele_attuali, env.record_mele, 
            w_tot, h_ui, slider_val
        )
        
        disegna_grafici_dashboard(
            dis, env.storico_mele, env.storico_passi, 
            w_tot, h_game, h_grafici, env.record_mele, env.record_passi
        )
        
        pygame.display.update()
        clock.tick(60)

# --- AVVIO DEL MAIN ---
if __name__ == '__main__':
    mp.freeze_support()
    
    pygame.init()
    dis = pygame.display.set_mode((800, 650), pygame.RESIZABLE)
    pygame.event.set_grab(False)
    porta_finestra_in_primo_piano()
    clock = pygame.time.Clock()

    env = SnakeEnv()
    try:
        model = PPO.load("snake_model")
        modello_caricato = True
    except:
        modello_caricato = False

    scelta = "MENU"
    while True:
        if scelta == "MENU":
            scelta = menu_iniziale()
            
        if scelta == "classico":
            scelta = loop_classico()
        elif scelta == "addestramento":
            scelta = loop_addestramento()
            
        if scelta == "QUIT" or scelta is None:
            break

    pygame.quit()