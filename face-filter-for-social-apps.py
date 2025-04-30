import cv2  
import numpy as np 

cap = cv2.VideoCapture(0)  # Kamerayı başlattık
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 540)  # Çözünürlüğü 9:16 oranına ayarlıyoruz (standart dikey video boyutu olduğu için)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

frame_count = 0  # Dalgalanma hareketi için sayaç 
effect_stage = 0  # Hangi efekti uygulayacağımızı takip eden sayaç

def apply_wave_effect(frame, horizontal=False, horizontal_lines=False, move_lines=False):
    """ Görüntüye dalgalanma veya çizgili efekt ekler """
    h, w, _ = frame.shape
    distorted_frame = np.zeros_like(frame)
    
    if horizontal:  # Yatay dalgalanma efekti
        for i in range(h):
            shift = int(15 * np.sin(2 * np.pi * (i / 150.0) + frame_count * 0.05))
            distorted_frame[i] = np.roll(frame[i], shift, axis=0)
    elif horizontal_lines:  # Yatay çizgilerle efekt
        for i in range(h):
            if i % 10 < 5:
                distorted_frame[i] = frame[i]
        if move_lines:  # Çizgileri hareket ettirmek için
            distorted_frame = np.roll(distorted_frame, int(frame_count * 1.4), axis=0)
    else:  # Dikey dalgalanma efekti 
        for i in range(w):
            shift = int(15 * np.sin(2 * np.pi * (i / 150.0) + frame_count * 0.05))
            distorted_frame[:, i] = np.roll(frame[:, i], shift, axis=0)
    
    return distorted_frame

def add_fire_effect(frame):  # Ateş efekti (Kırmızı ton ve dalgalanma)
    overlay = apply_wave_effect(frame.copy(), horizontal=True)
    red_tone = np.zeros_like(overlay)
    red_tone[:, :, 2] = 255  # RGB ile kırmızı tonu ekledik
    return cv2.addWeighted(overlay, 0.6, red_tone, 0.4, 0)

def add_air_effect(frame):  # Hava efekti (Mercek görünümü)
    overlay = frame.copy()
    h, w, _ = overlay.shape
    center_x, center_y = w // 2, h // 2
    radius = 100  # Mercek büyüklüğü

    mask = np.zeros_like(overlay, dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)  # Mercek alanı oluşturmak için
    mask = cv2.GaussianBlur(mask, (21, 21), 0)  # Kenarları yumuşattık
    overlay = cv2.addWeighted(overlay, 0.7, mask, 0.5, 0)
    
    zoomed = overlay[center_y - radius:center_y + radius, center_x - radius:center_x + radius]
    zoomed = cv2.resize(zoomed, (w, h), interpolation=cv2.INTER_LINEAR)
    return cv2.addWeighted(overlay, 0.8, zoomed, 0.2, 0)

def add_water_effect(frame):  # Su efekti (Mavi ton ve dalgalanma)
    overlay = apply_wave_effect(frame.copy())
    blue_tone = np.zeros_like(overlay)
    blue_tone[:, :, 0] = 255  # Mavi tonu eklemek için
    return cv2.addWeighted(overlay, 0.7, blue_tone, 0.3, 0)

def add_earth_effect(frame):  # Toprak efekti (Kahverengi ton ve çizgiler)
    overlay = apply_wave_effect(frame.copy(), horizontal_lines=True, move_lines=True)
    brown_tone = np.zeros_like(overlay)
    brown_tone[:, :, 2] = 50
    brown_tone[:, :, 1] = 25
    return cv2.addWeighted(overlay, 0.7, brown_tone, 0.3, 0)

dragging = False  # Fare tıklama durumu kontrolü

def mouse_callback(event, x, y, flags, param):  # Fare tıklamasıyla efekt değiştireceğiz
    global dragging, effect_stage
    if event == cv2.EVENT_LBUTTONDOWN:
        dragging = True
    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        effect_stage = (effect_stage + 1) % 4  # Efekt sırasını değiştiriyoruz

cv2.namedWindow("4 Element Efekti")  # Pencere oluşturduk
cv2.setMouseCallback("4 Element Efekti", mouse_callback)  # Mouse event bağladık

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if dragging:  # Efektleri uyguluyoruz
        if effect_stage == 0:
            frame = add_fire_effect(frame)
        elif effect_stage == 1:
            frame = add_air_effect(frame)
        elif effect_stage == 2:
            frame = add_water_effect(frame)
        elif effect_stage == 3:
            frame = add_earth_effect(frame)
    
    cv2.imshow("4 Element Efekti", frame)  # Görüntü gösterimi
    frame_count += 1  # Hareket efektleri için sayaç artırdık
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' tuşuna basılınca çıkış
        break

cap.release()
cv2.destroyAllWindows()
