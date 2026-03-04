import cv2
import mediapipe as mp
import math
import pyautogui
import time

# --- PERFORMANS AYARLARI ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0 # Komutlar arası zorunlu beklemeyi sıfırladık
screen_w, screen_h = pyautogui.size()

# Ayarlarına dokunulmadı
margin = 200          
smoothening = 7       
click_ratio = 0.15    
lock_threshold = 12     
escape_threshold = 45   

is_locked = False
anchor_x, anchor_y = 0, 0
prev_tx, prev_ty = 0, 0 
plocX, plocY = 0, 0 
clocX, clocY = 0, 0 

# KONTROLCÜLER
drag_active = False   
sol_tik_aktif = False # Mutex kilidi için eklendi
# -------------------------

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2, 
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

print("Turbo Performans Modu: Ayrı Parmak Kontrolleri Eklendi!")
print("- Tıklama Eli: İşaret(Sol Tık), Orta(Sağ Tık), Yüzük(Sürükle)")

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.resize(img, (640, 480))
    img = cv2.flip(img, 1) 
    h, w, c = img.shape
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    sol_el_hareket_ediyor = False
    sag_el_sol_tik = False
    sag_el_sag_tik = False
    sag_el_surukle = False # Yüzük parmağı değişkenimiz

    if results.multi_hand_landmarks and results.multi_handedness:
        for handLms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            el_taraf = handedness.classification[0].label 
            landmarks = handLms.landmark
            
            # 1. SOL EL (İmleç Hareketi ve Çapa)
            if el_taraf == "Right":  
                sol_el_hareket_ediyor = True
                x8, y8 = int(landmarks[8].x * w), int(landmarks[8].y * h)
                tx = (x8 - margin) * screen_w / (w - 2 * margin)
                ty = (y8 - margin) * screen_h / (h - 2 * margin)
                
                raw_speed = math.hypot(tx - prev_tx, ty - prev_ty)
                if not is_locked:
                    if raw_speed < lock_threshold:
                        is_locked = True
                        anchor_x, anchor_y = tx, ty
                else:
                    if math.hypot(tx - anchor_x, ty - anchor_y) > escape_threshold:
                        is_locked = False
                prev_tx, prev_ty = tx, ty

                if is_locked:
                    tx, ty = anchor_x, anchor_y
                    cv2.circle(img, (x8, y8), 12, (255, 255, 255), cv2.FILLED) 
                else:
                    cv2.circle(img, (x8, y8), 10, (255, 0, 0), cv2.FILLED) 

                clocX = plocX + (tx - plocX) / smoothening
                clocY = plocY + (ty - plocY) / smoothening
                mouse_x = max(0, min(screen_w, int(clocX)))
                mouse_y = max(0, min(screen_h, int(clocY)))
                plocX, plocY = clocX, clocY

            # 2. SAĞ EL (Butonlar)
            elif el_taraf == "Left": 
                x0, y0, x9, y9 = int(landmarks[0].x*w), int(landmarks[0].y*h), int(landmarks[9].x*w), int(landmarks[9].y*h)
                ref_mesafe = math.hypot(x9 - x0, y9 - y0) or 1
                
                # Yüzük parmağının ucunu (16) da hesaplamaya kattık
                x4, y4 = int(landmarks[4].x*w), int(landmarks[4].y*h)
                x8, y8 = int(landmarks[8].x*w), int(landmarks[8].y*h)
                x12, y12 = int(landmarks[12].x*w), int(landmarks[12].y*h)
                x16, y16 = int(landmarks[16].x*w), int(landmarks[16].y*h)
                
                # İşaret (Tek Tık)
                if (math.hypot(x8 - x4, y8 - y4) / ref_mesafe) < click_ratio:
                    sag_el_sol_tik = True
                    cv2.circle(img, (x8, y8), 12, (0, 255, 0), cv2.FILLED) 
                
                # Orta (Sağ Tık)
                if (math.hypot(x12 - x4, y12 - y4) / ref_mesafe) < click_ratio:
                    sag_el_sag_tik = True
                    cv2.circle(img, (x12, y12), 12, (0, 0, 255), cv2.FILLED) 

                # Yüzük (Sürükle)
                if (math.hypot(x16 - x4, y16 - y4) / ref_mesafe) < click_ratio:
                    sag_el_surukle = True
                    cv2.circle(img, (x16, y16), 12, (255, 255, 0), cv2.FILLED)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # --- KRİTİK İŞLEM ALANI (KİLİTLİ MANTIK) ---
    if sol_el_hareket_ediyor:
        pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
        
        # 1. ÖNCELİK: SÜRÜKLE VE BIRAK (Yüzük Parmağı)
        if sag_el_surukle:
            if not drag_active:
                pyautogui.mouseDown(button='left')
                drag_active = True
            
            # Sürüklerken işaret parmağının araya girip tıklamasını engeller
            sol_tik_aktif = True 
        else:
            if drag_active:
                pyautogui.mouseUp(button='left')
                drag_active = False

            # 2. ÖNCELİK: NORMAL SOL TIK (İşaret Parmağı)
            # Sadece yüzük parmağı havada ise (sürükleme yoksa) çalışır
            if sag_el_sol_tik:
                if not sol_tik_aktif:
                    pyautogui.click() # Doğrudan kusursuz tık
                    sol_tik_aktif = True
            else:
                sol_tik_aktif = False

        # 3. BAĞIMSIZ GÖREV: SAĞ TIK (Orta Parmak)
        if sag_el_sag_tik and not drag_active:
            pyautogui.rightClick()
            time.sleep(0.2) 

    cv2.imshow("Sanal Fare - Turbo Mod", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()