# Juego: Bicicleta con obstáculos

Juego sencillo hecho con Pygame. El jugador controla una bicicleta (rectángulo) con las teclas de dirección. Los obstáculos (círculos) aparecen aleatoriamente desde arriba. El jugador obtiene 0,5 segundos de invulnerabilidad cada vez que cambia de pantalla desplazándose hacia arriba (ganando 10 puntos por avance). A los 40 segundos aparece un perro que persigue al jugador durante 15 segundos; tras aparecer espera 0,1 segundos antes de comenzar a atacar y, una vez activo, se comporta con un retraso de 0,5 segundos respecto a la posición del jugador para hacer la persecución más desafiante. Al chocar con un obstáculo o con el perro, el jugador pierde una vida (tiene 5 al inicio), se vuelve invulnerable 1 segundo y pierden 30 puntos. Por cada 50 puntos acumulados, el jugador gana una vida adicional.

## Controles

- Flechas: mover arriba/abajo/izquierda/derecha
- R: reiniciar después de Game Over

## Requisitos

Instala las dependencias e ejecuta:

```bash
pip install -r requirements.txt
python main.py
```
