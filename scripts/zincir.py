# zincir.py: clip chaining helper (CPU only, no GPU, no network). Klip zincirleme yardimcisi (yalniz CPU).
# EN: three subcommands. `plan` turns a target length into a clip plan; `son-kare` extracts the REAL last frame
#   of a clip (index N-1, counted, not guessed by time); `bagla` prints (or with --calistir runs) the ffmpeg
#   command that joins clips and drops the duplicated hand-off frame. It never starts the engine.
# TR: uc alt komut. `plan` hedef sureyi klip planina cevirir; `son-kare` klibin GERCEK son karesini (N-1. kare,
#   sayilarak) cikarir; `bagla` klipleri birlestiren ve devir karesini atan ffmpeg komutunu yazdirir (--calistir ile calistirir).
# Run: python -I -X utf8 scripts/zincir.py plan --sure 30
# Exit codes: 0 ok, 2 bad input (file missing, too short, unreadable), 3 ffmpeg/ffprobe not found.
# Evidence: docs/SIK_HATALAR.md item 9 (wrong last frame gave seam SSIM 0.659) [read]; recipes: docs/KLIP_ZINCIRI.md.
# Not measured by us: the quality of any chained film (seams are checked by eye and by scripts/dikis_denetim.py) [not tried].
import argparse
import os
import re
import shutil
import subprocess
import sys

FPS = 24
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sabit(ad, varsayilan):
    """uret.ps1 tek-sabit satirindan oku ($KareInit = 192 gibi); okunamazsa varsayilan. Sayiyi kopyalamamak icin."""
    try:
        with open(os.path.join(KOK, 'scripts', 'uret.ps1'), encoding='utf-8', errors='replace') as f:
            m = re.search(r'^\$%s\s*=\s*(\d+)' % re.escape(ad), f.read(), re.M)
        return int(m.group(1)) if m else varsayilan
    except OSError:
        return varsayilan


def _arac(ad):
    env = os.environ.get('VT_FFMPEG') if ad == 'ffmpeg' else None
    yol = env if env and os.path.isfile(env) else None
    if ad == 'ffprobe' and os.environ.get('VT_FFMPEG'):
        kardes = os.path.join(os.path.dirname(os.environ['VT_FFMPEG']), 'ffprobe.exe')
        yol = kardes if os.path.isfile(kardes) else None
    return yol or shutil.which(ad)


def _yok(ad):
    print('HATA: %s bulunamadi. winget install Gyan.FFmpeg ya da VT_FFMPEG=<ffmpeg.exe yolu> ayarlayin (%s not found).' % (ad, ad), file=sys.stderr)
    return 3


def kare_sayisi(video, ffprobe):
    """Sayilan kare sayisi (-count_frames); okunamazsa None."""
    try:
        r = subprocess.run([ffprobe, '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                            '-show_entries', 'stream=nb_read_frames', '-of', 'default=nw=1:nk=1', video],
                           capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError):
        return None
    s = r.stdout.strip().splitlines()
    return int(s[0]) if r.returncode == 0 and s and s[0].isdigit() else None


def kare_gecerli(n):
    return n >= 5 and (n - 5) % 17 == 0


def komut_plan(a):
    init = _sabit('KareInit', 192)
    kare = a.kare if a.kare else init
    if a.sure <= 0:
        print('HATA: --sure sifirdan buyuk olmali (saniye).', file=sys.stderr)
        return 2
    if not kare_gecerli(kare) or kare > init:
        print('HATA: --kare 17k+5 olmali (5, 22, ... 192) ve en fazla %d (uret.ps1 -InitImg tavani). Verilen: %d' % (init, kare), file=sys.stderr)
        return 2
    ilk = _sabit('KareSabit', 209)
    net = (kare - 1) / FPS          # devam kliplerinde ilk kare (devir karesi) atilir
    ilk_s = ilk / FPS
    if a.sure <= ilk_s:
        print('Tek klip yeter: -Kare %d en fazla (%.1f sn). Zincir gerekmez.' % (ilk, ilk_s))
        return 0
    kalan = a.sure - ilk_s
    ek = int(-(-kalan // net))
    print('Hedef %.1f sn, %d fps.' % (a.sure, FPS))
    print('Klip 1: metinden (-Kare %d, %.1f sn). Klip 2..%d: -InitImg ile (-Kare %d, her biri net %.2f sn = %d kare, devir karesi atilir).' % (ilk, ilk_s, ek + 1, kare, net, kare - 1))
    print('Toplam %d klip, en az %.1f sn (son klip kirpilabilir). Her klipten sonra: python -I -X utf8 scripts/zincir.py son-kare <klip> <png>' % (ek + 1, ilk_s + ek * net))
    print('Sure tahmini YOK: bu kartta zincir olcumu yapilmadi [not tried]; tek klip sureleri docs/OLCUMLER.md.')
    return 0


def komut_son_kare(a):
    ffprobe, ffmpeg = _arac('ffprobe'), _arac('ffmpeg')
    if not ffprobe or not ffmpeg:
        return _yok('ffmpeg/ffprobe')
    if not os.path.isfile(a.video) or os.path.getsize(a.video) == 0:
        print('HATA: video yok ya da bos: %s' % a.video, file=sys.stderr)
        return 2
    n = kare_sayisi(a.video, ffprobe)
    if n is None or n < 2:
        print('HATA: kare sayisi okunamadi ya da 2den az (%s): %s' % (n, a.video), file=sys.stderr)
        return 2
    if os.path.exists(a.cikti) and not a.uzerine:
        print('HATA: cikti zaten var (ustune yazmak icin --uzerine): %s' % a.cikti, file=sys.stderr)
        return 2
    r = subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', a.video, '-vf', 'select=eq(n\\,%d)' % (n - 1),
                        '-vsync', '0', '-frames:v', '1', '-update', '1', a.cikti], capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.isfile(a.cikti) or os.path.getsize(a.cikti) == 0:
        print('HATA: son kare yazilamadi: %s' % r.stderr.strip()[:200], file=sys.stderr)
        return 2
    print('TAMAM: %d kareli klibin %d. (son, 0 tabanli) karesi yazildi: %s' % (n, n - 1, a.cikti))
    return 0


def ses_var(video, ffprobe):
    """True/False: does the clip have an audio stream; None if unreadable."""
    try:
        r = subprocess.run([ffprobe, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                            '-of', 'csv=p=0', video], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(r.stdout.strip()) if r.returncode == 0 else None


def ps_tirnak(s):
    """PowerShell single-quoted literal: nothing inside is expanded ($, backtick, ;, [ are safe).
    PowerShell treats ' and the typographic single quotes U+2018, U+2019, U+201A, U+201B all as quote marks,
    so every one of them is doubled (otherwise a file name like x\u2019;calc;\u2018.mp4 would break out)."""
    return "'" + re.sub("['\u2018\u2019\u201a\u201b]", lambda m: m.group(0) * 2, s) + "'"


def bagla_komutu(klipler, cikti, sesli=True):
    giris = []
    for k in klipler:
        giris += ['-i', k]
    f = []
    for i in range(len(klipler)):
        v = '[%d:v]%ssetpts=PTS-STARTPTS,fps=%d[v%d]' % (i, 'trim=start_frame=1,' if i else '', FPS, i)
        f.append(v)
    f.append(''.join('[v%d]' % i for i in range(len(klipler))) + 'concat=n=%d:v=1:a=0[v]' % len(klipler))
    ses = []
    for i in range(len(klipler) if sesli else 0):
        ses.append('[%d:a]%saresample=48000,asetpts=PTS-STARTPTS[a%d]' % (i, 'atrim=start=%.4f,' % (1.0 / FPS) if i else '', i))
    f += ses
    if sesli:
        f.append(''.join('[a%d]' % i for i in range(len(klipler))) + 'concat=n=%d:v=0:a=1[a]' % len(klipler))
        cikis = ['-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                 '-c:a', 'aac', '-b:a', '160k', '-ar', '48000']
    else:
        cikis = ['-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p']
    return (['-filter_complex', ';'.join(f)] + cikis, giris)


def komut_bagla(a):
    if len(a.klip) < 2:
        print('HATA: en az 2 klip gerekir.', file=sys.stderr)
        return 2
    for k in a.klip:
        if not os.path.isfile(k) or os.path.getsize(k) == 0:
            print('HATA: klip yok ya da bos: %s' % k, file=sys.stderr)
            return 2
    ffmpeg, ffprobe = _arac('ffmpeg'), _arac('ffprobe')
    if (not ffmpeg or not ffprobe) and a.calistir:
        return _yok('ffmpeg/ffprobe')
    sesli = True
    if ffprobe:
        durum = [ses_var(k, ffprobe) for k in a.klip]
        if None in durum:
            print('HATA: ses akisi okunamadi (bozuk klip?): %s' % a.klip[durum.index(None)], file=sys.stderr)
            return 2
        if any(durum) and not all(durum):
            print('HATA: bazi klipler sesli, bazilari sessiz; hepsi ayni olmali. Sessiz olanlar: %s' % ', '.join(k for k, v in zip(a.klip, durum) if not v), file=sys.stderr)
            return 2
        sesli = all(durum)
    sonra, giris = bagla_komutu(a.klip, a.cikti, sesli)
    komut = [ffmpeg or 'ffmpeg', '-hide_banner', '-v', 'error', '-y'] + giris + sonra + [a.cikti]
    print('PowerShell:')
    print('& ' + ' '.join(ps_tirnak(x) for x in komut))
    print('Ses: %s' % ('var (birlestirilir)' if sesli else 'yok (yalniz video, -an)'))
    print('Sonra dikisi kontrol edin: python -I -X utf8 scripts/dikis_denetim.py ' + ' '.join(ps_tirnak(x) for x in a.klip))
    if a.calistir:
        if os.path.exists(a.cikti) and not a.uzerine:
            print('HATA: cikti zaten var (--uzerine): %s' % a.cikti, file=sys.stderr)
            return 2
        r = subprocess.run(komut)
        return 0 if r.returncode == 0 else 2
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description='VideoTurko clip chaining helper (CPU only).')
    s = p.add_subparsers(dest='cmd', required=True)
    a = s.add_parser('plan'); a.add_argument('--sure', type=float, required=True); a.add_argument('--kare', type=int, default=0)
    b = s.add_parser('son-kare'); b.add_argument('video'); b.add_argument('cikti'); b.add_argument('--uzerine', action='store_true')
    c = s.add_parser('bagla'); c.add_argument('klip', nargs='+'); c.add_argument('-o', '--cikti', default='film.mp4')
    c.add_argument('--calistir', action='store_true'); c.add_argument('--uzerine', action='store_true')
    arg = p.parse_args(argv)
    return {'plan': komut_plan, 'son-kare': komut_son_kare, 'bagla': komut_bagla}[arg.cmd](arg)


if __name__ == '__main__':
    sys.exit(main())
