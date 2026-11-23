"""Klip sonu sicrama denetimi (BILGI, kapi degil): python -I son_kare_denetim.py klip.avi|mp4 [...]

Son karelerde yuz/nesne aniden baska bir seye donusuyorsa bunu sayiyla gosterir ve kac kare tutulabilecegini onerir.
Kalite kapisinin kararini degistirmez; SUPHELI yalniz "klibin sonunu izle" demektir.

Olcum: kareler gri ve 96 px genislige kucultulur (ince gren etkisi azalir).
  sicrama = son 8 kare gecisindeki en buyuk degisim / klibin ortasindaki tipik degisim
  son8    = son kare ile 8 kare oncesi farki / tipik 8 kare farki
SUPHELI: sicrama >= 5.0 VE son8 >= 2.5. Esikler 27 klipte [olctum] secildi, genel esik degildir.
Cikis: 0 = olcum yapildi (SUPHELI dahil); 3 = girdi hatasi; 6 = opencv/numpy yok.
"""
import os
import sys

KUYRUK = 8
SICRAMA_ESIK = 5.0
SON8_ESIK = 2.5
BASLANGIC_ESIK = 2.0
EN_AZ_KARE = 24


def olc(gri):
    """gri: ayni boyutta 2B numpy kareleri. Olcum sozlugu dondurur."""
    import numpy as np
    k = [x.astype("float32") for x in gri]
    d1 = np.array([np.abs(k[j] - k[j - 1]).mean() for j in range(1, len(k))])
    taban = max(float(np.median(d1[4:-KUYRUK])), 1e-6)
    kuyruk = d1[-KUYRUK:]
    sicrama = float(kuyruk.max()) / taban
    tepe_kare = len(d1) - KUYRUK + int(kuyruk.argmax()) + 1
    d8 = np.array([np.abs(k[j] - k[j - KUYRUK]).mean() for j in range(KUYRUK, len(k))])
    son8 = float(d8[-1]) / max(float(np.median(d8[:-4])), 1e-6)
    supheli = sicrama >= SICRAMA_ESIK and son8 >= SON8_ESIK
    tut = len(k)
    if supheli:
        # Tepeden geriye yuru. Degisim kare atlayarak gelebildigi icin onceki iki adima birlikte bakilir.
        j = tut = tepe_kare - 1
        while j - 2 >= len(d1) // 2 and max(d1[j - 1], d1[j - 2]) >= BASLANGIC_ESIK * taban:
            j -= 1 if d1[j - 1] >= BASLANGIC_ESIK * taban else 2
        tut = j + 1
    return {"kare": len(k), "sicrama": sicrama, "tepe_kare": tepe_kare, "son8": son8, "supheli": supheli, "tut": tut}


def oku(yol, cv2):
    c = cv2.VideoCapture(yol)
    g = []
    while True:
        r, x = c.read()
        if not r:
            break
        y = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
        g.append(cv2.resize(y, (96, max(2, round(y.shape[0] * 96 / y.shape[1]))), interpolation=cv2.INTER_AREA))
    c.release()
    return g


def main(arg):
    if not arg or any(a.startswith("-") for a in arg):
        print("Kullanim: python -I son_kare_denetim.py klip.avi|mp4 [...]")
        return 3
    for p in arg:
        if not os.path.isfile(p):
            print("HATA: dosya yok: %s" % os.path.basename(p))
            return 3
    try:
        import cv2
        import numpy  # noqa: F401
    except ImportError as e:
        print("KAPI CALISMADI: opencv-python/numpy yok (%s)" % e)
        return 6
    for p in arg:
        g = oku(p, cv2)
        if len(g) < EN_AZ_KARE:
            print("HATA: %s okunamadi ya da cok kisa (%d kare, en az %d)" % (os.path.basename(p), len(g), EN_AZ_KARE))
            return 3
        o = olc(g)
        karar = "SUPHELI: klibin sonunu izle, ilk %d kare tutulabilir" % o["tut"] if o["supheli"] else "normal"
        print("SON_KARE (bilgi, kapi degil): %s kare=%d sicrama=%.2f (kare %d) son8=%.2f sonuc=%s" % (
            os.path.basename(p), o["kare"], o["sicrama"], o["tepe_kare"], o["son8"], karar))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
