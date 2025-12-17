from assets.images import coin_img

def draw_coins(surface, coins):
    for coin in coins:
        surface.blit(coin_img, coin.topleft)
