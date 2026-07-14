import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import json
import os

class SnakeEnv(gym.Env):
    def __init__(self):
        super(SnakeEnv, self).__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(28,), dtype=np.float32)
        
        # Dimensioni della griglia di gioco speculari a quelle usate in main.py
        self.larghezza = 800
        self.altezza = 490
        self.min_y = 100
        self.blocco = 20
        
        self.carica_statistiche()
        self.reset()

    def carica_statistiche(self):
        if os.path.exists("stats.json"):
            try:
                with open("stats.json", "r") as f:
                    dati = json.load(f)
                    self.iterazioni = dati.get("iterazioni", 0)
                    self.passi_totali = dati.get("passi_totali", 0)
                    self.storico_mele = dati.get("storico_mele", [])
                    self.storico_passi = dati.get("storico_passi", [])
                    self.record_mele = dati.get("record_mele", 0)
                    self.record_passi = dati.get("record_passi", 0)
            except:
                self.inizializza_statistiche_vuote()
        else:
            self.inizializza_statistiche_vuote()
            
        self.premio = 0

    def Casino_inizializza_statistiche_vuote(self):
        self.iterazioni = 0
        self.passi_totali = 0
        self.storico_mele = []
        self.storico_passi = []
        self.record_mele = 0
        self.record_passi = 0
        self.premio = 0

    def inizializza_statistiche_vuote(self):
        self.Casino_inizializza_statistiche_vuote()

    def salva_statistiche(self):
        dati = {
            "iterazioni": self.iterazioni,
            "passi_totali": self.passi_totali,
            "storico_mele": self.storico_mele,
            "storico_passi": self.storico_passi,
            "record_mele": self.record_mele,
            "record_passi": self.record_passi
        }
        try:
            with open("stats.json", "w") as f:
                json.dump(dati, f)
        except:
            pass

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Posizionamento centrale sicuro dentro lo spazio utile
        x1 = self.larghezza // 2 // self.blocco * self.blocco
        y1 = ((self.altezza + self.min_y) // 2) // self.blocco * self.blocco
        
        self.snake = [[x1, y1], [x1 - self.blocco, y1], [x1 - 2 * self.blocco, y1]]
        self.direction_x = self.blocco
        self.direction_y = 0
        
        self.frame_iteration = 0
        self.genera_mela()
        
        # Salviamo la distanza iniziale per calcolare l'avvicinamento al passo successivo
        self.vecchia_distanza = np.linalg.norm(np.array(self.snake[0]) - np.array(self.apple))
        
        return self._get_obs(), {}

    def genera_mela(self):
        max_grid_x = (self.larghezza // self.blocco) - 1
        max_grid_y = (self.altezza // self.blocco) - 1
        min_grid_y = self.min_y // self.blocco
        
        while True:
            m_x = random.randint(0, max_grid_x) * self.blocco
            m_y = random.randint(min_grid_y, max_grid_y) * self.blocco
            if [m_x, m_y] not in self.snake:
                self.apple = [m_x, m_y]
                break

    def _get_obs(self):
        testa_x, testa_y = self.snake[0]
        stato = []
        direzioni = [
            (0, -self.blocco), (0, self.blocco), (-self.blocco, 0), (self.blocco, 0),
            (-self.blocco, -self.blocco), (self.blocco, -self.blocco), (-self.blocco, self.blocco), (self.blocco, self.blocco)
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
                
                if x < 0 or x >= self.larghezza or y < self.min_y or y >= self.altezza:
                    dist_muro = 1.0 / step
                    break
                    
                if dist_corpo == 0.0 and [x, y] in self.snake[:-1]:
                    dist_corpo = 1.0 / step
                    
                if dist_mela == 0.0 and x == self.apple[0] and y == self.apple[1]:
                    dist_mela = 1.0 / step
                    
                step += 1
                
            stato.extend([dist_muro, dist_mela, dist_corpo])
            
        dir_u = int(self.direction_y == -self.blocco)
        dir_d = int(self.direction_y == self.blocco)
        dir_l = int(self.direction_x == -self.blocco)
        dir_r = int(self.direction_x == self.blocco)
        
        stato.extend([dir_u, dir_l, dir_d, dir_r])
        return np.array(stato, dtype=np.float32)

    def step(self, action):
        self.frame_iteration += 1
        self.passi_totali += 1
        
        # 0 = SU, 1 = SINISTRA, 2 = GIÙ, 3 = DESTRA
        if action == 0 and self.direction_y != self.blocco:
            self.direction_x, self.direction_y = 0, -self.blocco
        elif action == 1 and self.direction_x != self.blocco:
            self.direction_x, self.direction_y = -self.blocco, 0
        elif action == 2 and self.direction_y != -self.blocco:
            self.direction_x, self.direction_y = 0, self.blocco
        elif action == 3 and self.direction_x != -self.blocco:
            self.direction_x, self.direction_y = self.blocco, 0
            
        head = [self.snake[0][0] + self.direction_x, self.snake[0][1] + self.direction_y]
        
        hit_wall = head[0] < 0 or head[0] >= self.larghezza or head[1] < self.min_y or head[1] >= self.altezza
        mangia_ora = (head == self.apple)
        corpo_da_controllare = self.snake if mangia_ora else self.snake[:-1]
        hit_self = head in corpo_da_controllare
        starved = self.frame_iteration > 100 * len(self.snake)
        
        if hit_wall or hit_self or starved:
            terminated = True
            if hit_self:
                self.premio -= 100
                reward = -2.0  # Penalità bilanciata per scontro interno
            elif hit_wall:
                self.premio -= 50
                reward = -1.5  # Penalità per scontro a muro
            else:
                self.premio -= 10
                reward = -1.0
                
            self.iterazioni += 1
            
            mele_mangiate = len(self.snake) - 3
            self.storico_mele.append(mele_mangiate)
            self.storico_passi.append(self.frame_iteration)
            
            if mele_mangiate > self.record_mele: self.record_mele = mele_mangiate
            if self.frame_iteration > self.record_passi: self.record_passi = self.frame_iteration

            self.storico_mele = self.storico_mele[-100:]
            self.storico_passi = self.storico_passi[-100:]
            
            self.salva_statistiche()
            obs = self.reset()[0]
            return obs, reward, terminated, False, {}
            
        self.snake.insert(0, head)
        
        if head == self.apple:
            self.premio += 10
            reward = 10.0  # <--- MODIFICA: Ricompensa molto alta per focalizzarsi sull'obiettivo vero!
            self.genera_mela()
        else:
            self.snake.pop()
            
            # Calcolo incentivo di avvicinamento alla mela
            nuova_distanza = np.linalg.norm(np.array(head) - np.array(self.apple))
            if nuova_distanza < self.vecchia_distanza:
                reward = 0.015
            else:
                reward = -0.015 # <--- MODIFICA: Penalità mitigata per permettere le manovre ad ampio raggio
            self.vecchia_distanza = nuova_distanza
            
            # Piccolo malus temporale per evitare che lo snake giri in tondo all'infinito
            reward -= 0.005
            
        self.salva_statistiche()
        return self._get_obs(), reward, False, False, {}