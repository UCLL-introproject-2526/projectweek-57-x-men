import pygame
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

pygame.init()

clip = VideoFileClip("video/end.mp4")
os.makedirs("video/end_frames", exist_ok=True)

for i, frame in enumerate(clip.iter_frames()):
    surf = pygame.surfarray.make_surface(frame.swapaxes(0,1))
    pygame.image.save(surf, f"video/end_frames/frame_{i:03}.png")

clip.close()
