# -import pygame
import sounddevice as sd
import numpy as np
import random
import math

# 初始化Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("自由扩散粒子效果")
clock = pygame.time.Clock()

# 粒子类
class Particle:
    def __init__(self, x, y, velocity, angle):
        self.x = x
        self.y = y
        self.size = random.uniform(1, 3)  # 粒子尺寸变小
        self.velocity = velocity
        self.angle = angle
        self.alpha = 255  # 初始透明度
        self.alpha_decay_rate = random.uniform(1, 3)  # 随机透明度衰减速率

    def move(self):
        # 自由扩散运动
        self.x += self.velocity * math.cos(self.angle) + random.uniform(-0.5, 0.5)  # 随机漂移
        self.y += self.velocity * math.sin(self.angle) + random.uniform(-0.5, 0.5)  # 随机漂移
        if self.velocity > 0.2:
            self.velocity *= 0.99  # 减速逻辑
        # 根据随机速率减少透明度
        self.alpha -= self.alpha_decay_rate
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        color = (255, 255, 255, int(self.alpha))  # 白色粒子，透明度随alpha变化
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (int(self.size), int(self.size)), int(self.size))
        surface.blit(particle_surface, (int(self.x), int(self.y)))

# 绘制渐变背景
def draw_gradient_background(surface):
    for y in range(HEIGHT):
        # 从深蓝 (#00001a) 到较深的蓝 (#000033)
        r = 0
        g = int(10 * (y / HEIGHT))  # 更深的绿色分量
        b = int(26 + (40 * y / HEIGHT))  # 更深的蓝色分量
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# 音量检测回调
def audio_callback(indata, frames, time, status):
    global volume
    volume = np.linalg.norm(indata)  # 计算音量幅值

volume = 0

# 开启音频输入流
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100)
stream.start()

# 粒子存储列表
particles = []

# 主循环
running = True
while running:
    screen.fill((0, 0, 0))  # 清空屏幕
    draw_gradient_background(screen)  # 绘制渐变背景

    # 只有当音量达到阈值时生成粒子
    if volume > 0.05:  # 灵敏度调整
        for _ in range(int(volume * 50)):  # 增加粒子密集度
            # 粒子从屏幕下方更深处生成，扇形扩散
            angle = random.uniform(-math.pi / 2 - math.pi / 4, -math.pi / 2 + math.pi / 4)  # 扇形扩散角度
            velocity = random.uniform(6, 12) + volume * 3  # 提高初始速度范围
            particles.append(Particle(WIDTH // 2, HEIGHT + 400, velocity, angle))  # 从更深处生成粒子

    # 更新和绘制粒子
    for particle in particles[:]:
        particle.move()
        particle.draw(screen)
        if particle.alpha <= 0:  # 粒子完全透明时移除
            particles.remove(particle)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)  # 限制帧率为60FPS

# 关闭音频流和退出Pygame
stream.stop()
pygame.quit()
