"""Переименование mokaGram -> ciraGram во всём дереве (включая сабмодули).
Запуск: python cira-cloud/rebrand.py <корень репозитория>
Авторство автора оставляется (лицензия GPLv3, см. MOKAGRAM_NOTICE.md)."""
import os, re, sys

root = os.path.abspath(sys.argv[1])
os.chdir(root)
if os.path.exists('MOKAGRAM_NOTICE.md'):
    os.remove('MOKAGRAM_NOTICE.md')

SKIP_NAMES = {'LICENSE', 'LEGAL'}
SKIP_DIRS = ('./.git', './Telegram/ThirdParty', './cira-cloud', './.github/windows-exe', './.github/workflows')
PROTECT = [
    r'https?://[^\s"\'<>)\]`]*moka[^\s"\'<>)\]`]*',
    r'(?:www\.)?github\.com/(?:mokagram|ecronx\w*)/[\w./-]*',
    r'[\w.-]*moka\.wtf[\w./-]*',
    r'@moka\w+',
    r't\.me/moka\w*',
]
prot_re = re.compile('|'.join('(?:%s)' % p for p in PROTECT))
moka_re = re.compile(r'moka', re.I)
MARK = re.compile(r'^[ \t]*// mokagram-id: [0-9a-f]+[ \t]*\r?\n', re.M)

def conv(m):
    s = m.group(0)
    return 'CIRA' if s.isupper() else ('Cira' if s[0].isupper() else 'cira')

def transform(text):
    text = re.sub(r'[\w.-]*moka\.wtf', 'cira.invalid', text)
    kept = []
    def stash(m):
        kept.append(m.group(0)); return '\x00%d\x00' % (len(kept) - 1)
    t = moka_re.sub(conv, prot_re.sub(stash, text))
    return re.sub('\x00(\\d+)\x00', lambda m: kept[int(m.group(1))], t)

def skipped(path):
    p = path.replace('\\', '/')
    return any(p == d or p.startswith(d + '/') for d in SKIP_DIRS)

files, paths = [], []
for dp, dns, fns in os.walk('.'):
    dns[:] = [d for d in dns if not skipped(os.path.join(dp, d))]
    for n in fns:
        f = os.path.join(dp, n)
        if n not in SKIP_NAMES and os.path.getsize(f) < 8 * 1024 * 1024:
            files.append(f)
    for n in dns + fns:
        if 'moka' in n.lower() and n not in SKIP_NAMES:
            paths.append(os.path.join(dp, n))

changed = 0
for f in files:
    try:
        txt = open(f, 'rb').read().decode('utf-8')
    except Exception:
        continue
    if 'moka' not in txt.lower():
        continue
    new = transform(MARK.sub('', txt))
    if new != txt:
        with open(f, 'w', encoding='utf-8', newline='') as o:
            o.write(new)
        changed += 1
print('content changed:', changed)

paths.sort(key=lambda p: -p.count(os.sep))
renamed = 0
for p in paths:
    d, n = os.path.split(p)
    q = os.path.join(d, moka_re.sub(conv, n))
    if not os.path.exists(q):
        os.rename(p, q); renamed += 1
print('paths renamed:', renamed)

def read_lf(path):
    """Текст файла с переводами строк \n (на Windows git может отдать \r\n) и признак CRLF."""
    s = open(path, encoding='utf-8', errors='surrogateescape', newline='').read()
    crlf = '\r\n' in s
    return s.replace('\r\n', '\n'), crlf

def write_lf(path, s, crlf):
    if crlf:
        s = s.replace('\n', '\r\n')
    open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)

def edit(path, old, new):
    if not os.path.exists(path):
        print('missing', path); return
    s, crlf = read_lf(path)
    if old in s and new not in s:
        write_lf(path, s.replace(old, new), crlf)
        print('edited', path)
    elif new not in s:
        print('NOT APPLIED', path, repr(old[:60]))

# окно «О программе»: оставляем только Telegram Desktop (его авторство снять нельзя)
ab = 'Telegram/SourceFiles/boxes/about_box.cpp'
if os.path.exists(ab):
    t, ab_crlf = read_lf(ab)
    t2 = re.sub(r'addText\(rpl::single\(\s*TextWithEntities\{ QString::fromUtf8\("ciraGram, автор "\) \}.*?"\)\)\)\);',
                'addText(rpl::single(TextWithEntities{ QString::fromUtf8("ciraGram. Основано на Telegram Desktop.") }));',
                t, count=1, flags=re.S)
    print('about box rewritten' if t2 != t else 'about box: pattern not found')
    write_lf(ab, t2, ab_crlf)
open('README.md', 'w', encoding='utf-8', newline='\n').write(
    "# ciraGram\n\nКлиент на основе Telegram Desktop (GPLv3) с плагинами, режимом призрака, "
    "сохранением удалённых сообщений, музыкальным плеером и другими функциями.\n\n"
    "Основано на [Telegram Desktop](https://github.com/telegramdesktop/tdesktop) "
    "(© The Telegram Desktop Authors, GPLv3 с исключением OpenSSL). Лицензия: см. файл LICENSE.\n")
edit('Telegram/Resources/winrc/Telegram.rc', 'VALUE "FileDescription", "Telegram Desktop"', 'VALUE "FileDescription", "ciraGram"')
edit('Telegram/Resources/winrc/Telegram.rc', 'VALUE "ProductName", "Telegram Desktop"', 'VALUE "ProductName", "ciraGram"')

edit('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp',
     'RefreshPage(0, std::make_shared<PagesState>(), fail);',
     'if (fail) { fail(); } // ciraGram: запросы к внешнему боту отключены')

# главное меню: убрать ссылки на канал, форум и репозиторий автора
mm = 'Telegram/SourceFiles/window/window_main_menu.cpp'
if os.path.exists(mm):
    t, mm_crlf = read_lf(mm)
    t = re.sub(r'links->setMarkedText\(.*?https://t\.me/mokaforum"_q\)\)\);', 'links->setText(QString());', t, count=1, flags=re.S)
    t = re.sub(r'tr::link\(\s*u"ciraGram Desktop"_q,\s*u"https://github\.com/mokagram/mokagram"_q\)',
               'TextWithEntities{ u"ciraGram Desktop"_q }', t, count=1)
    write_lf(mm, t, mm_crlf)

# общая функция запросов к внешнему боту: отключаем целиком
edit('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp',
     '\tconst auto botId = UserId(8687512401LL);\n',
     '\t// ciraGram: внешний бот отключён, запросы никуда не уходят\n\t(void)session;\n\t(void)query;\n\t(void)done;\n\tif (fail) {\n\t\tfail();\n\t}\n\treturn;\n\tconst auto botId = UserId(8687512401LL);\n')

# Файлы *.inc с Python-кодом плагинов хранят текст массивом байт (чтобы обойти предел MSVC на длину строки).
# Обычная замена текста их не видит: разбираем массив, меняем текст внутри и собираем обратно в том же виде.
def fix_byte_inc(path):
    t = open(path, encoding='utf-8', errors='surrogateescape').read()
    head = t[:t.find('{')]
    m = re.match(r'\s*constexpr char (\w+)\[\] = $', head)
    if not m:
        return False
    nums = re.findall(r'-?\d+', t[t.find('{') + 1:t.rfind('}')])
    if len(nums) < 20:
        return False
    data = bytes((int(x) & 255) for x in nums)
    if b'moka' not in data.lower():
        return False
    body, tail = (data[:-1], b'\0') if data.endswith(b'\0') else (data, b'')
    try:
        new = transform(body.decode('utf-8')).encode('utf-8') + tail
    except UnicodeDecodeError:
        return False
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('constexpr char %s[] = {\n' % m.group(1))
        for i in range(0, len(new), 24):
            f.write('\t' + ', '.join(str(b - 256 if b > 127 else b) for b in new[i:i + 24]) + ',\n')
        f.write('};\n')
    return True

fixed = 0
for dp, dns, fns in os.walk('Telegram/SourceFiles'):
    for n in fns:
        if n.endswith('.inc') and fix_byte_inc(os.path.join(dp, n)):
            fixed += 1
print('byte-array .inc fixed:', fixed)

# ссылки и кнопки, ведущие к автору: канал, форум, донаты, заголовки запросов, резервный список галочек
def sub_file(path, pattern, repl, flags=0):
    if not os.path.exists(path):
        print('missing', path); return
    t, crlf = read_lf(path)
    t2, n = re.subn(pattern, repl, t, flags=flags)
    print('sub', path, n)
    if n:
        write_lf(path, t2, crlf)

sm = 'Telegram/SourceFiles/settings/sections/settings_main.cpp'
sub_file(sm, r'[ \t]*builder\.addButton\(\{\s*\.id = u"main/(?:channel|forum)"_q,.*?\}\);\s*\n', '', re.S)
sub_file(sm, r'(const auto ways = std::vector<Way>\{)\s*.*?\n([ \t]*\};)', r'\1\n\2', re.S)
sub_file('Telegram/SourceFiles/ciragram/music/ciragram_lyrics.cpp',
         r'ciraGram \(https://github\.com/ecronx/mokagram\)', 'ciraGram')
sub_file('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp',
         r'https://raw\.githubusercontent\.com/mokagram/mokagram/badges/badges\.json', 'https://cira.invalid/badges.json')

# --- Язык: если язык Telegram ещё не выбран (первый запуск), берём язык Windows ---
lang_cpp = 'Telegram/SourceFiles/ciragram/lang/ciragram_lang.cpp'
edit(lang_cpp, '#include <QtCore/QProcessEnvironment>\n',
     '#include <QtCore/QProcessEnvironment>\n#include <QtCore/QLocale>\n')
sub_file(lang_cpp,
         r'(\tif \(id\.isEmpty\(\)\) \{\n)(?:\t\t//[^\n]*\n)+\t\treturn 2;\n',
         r'\1\t\t// ciraGram: язык Telegram ещё не выбран, ориентируемся на язык системы.\n'
         r'\t\tconst auto system = QLocale::system().name();\n'
         r'\t\treturn (system.startsWith(u"ru") || system.startsWith(u"uk") || system.startsWith(u"be")) ? 1 : 2;\n')

# --- Нагрузка: серверы галочек отключены, не опрашиваем их каждые 3 секунды ---
edit('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp',
     '\tLoad();\n\tstatic auto lifetime = rpl::lifetime();\n',
     '\tLoad();\n\treturn; // ciraGram: серверы галочек отключены, фоновый опрос не нужен\n\tstatic auto lifetime = rpl::lifetime();\n')

# --- Python в папке python\ рядом с ciraGram.exe (в корне остаются только exe, modules и python) ---
edit('Telegram/SourceFiles/ciragram/plugins/ciragram_plugins.cpp',
     'swprintf(name, 32, L"python%d%d.dll", PY_MAJOR_VERSION, PY_MINOR_VERSION);\n',
     'swprintf(name, 32, L"python%d%d.dll", PY_MAJOR_VERSION, PY_MINOR_VERSION);\n'
     '\t\t// ciraGram: встроенный Python лежит в папке python рядом с клиентом.\n'
     '\t\t// Загружаем его по полному пути: отложенная загрузка потом найдёт уже загруженную библиотеку,\n'
     '\t\t// а Python возьмёт python3NN._pth рядом с ней и найдёт свою стандартную библиотеку.\n'
     '\t\t{\n'
     '\t\t\tstatic wchar_t path[4096];\n'
     '\t\t\tconst auto length = GetModuleFileNameW(nullptr, path, 4096);\n'
     '\t\t\tif (length > 0 && length < 4000) {\n'
     '\t\t\t\tif (const auto slash = wcsrchr(path, L\'\\\\\')) {\n'
     '\t\t\t\t\tslash[1] = 0;\n'
     '\t\t\t\t\twcscat_s(path, 4096, L"python\\\\");\n'
     '\t\t\t\t\twcscat_s(path, 4096, name);\n'
     '\t\t\t\t\tif (LoadLibraryExW(path, nullptr, LOAD_WITH_ALTERED_SEARCH_PATH) != nullptr) {\n'
     '\t\t\t\t\t\treturn true;\n'
     '\t\t\t\t\t}\n'
     '\t\t\t\t}\n'
     '\t\t\t}\n'
     '\t\t}\n')

# --- Иконки в меню «Иконка приложения»: новые варианты ciraGram вместо mokaGram ---
icons_inc = 'Telegram/SourceFiles/ciragram/misc/ciragram_app_icons.inc'
if os.path.exists(icons_inc):
    from io import BytesIO
    try:
        from PIL import Image
    except ImportError:
        Image = None
    order = ['classic', 'fill', 'outline', 'black', 'white', 'sticker']
    icon_dir = os.path.join('cira-cloud', 'icons')
    lines = ['// Иконки приложения (выбор в настройках), 256x256 PNG, логотип ciraGram.']
    for i, name in enumerate(order):
        src = os.path.join(icon_dir, name + '.png')
        if Image:
            buf = BytesIO()
            Image.open(src).convert('RGBA').resize((256, 256), Image.LANCZOS).save(buf, 'PNG', optimize=True)
            data = buf.getvalue()
        else:
            data = open(src, 'rb').read()
        lines.append('constexpr unsigned char kAppIcon%d[] = {' % i)
        for j in range(0, len(data), 24):
            lines.append(','.join(str(b) for b in data[j:j + 24]) + ',')
        lines.append('};')
    lines.append('constexpr const unsigned char *kAppIcons[] = { %s };' % ', '.join('kAppIcon%d' % i for i in range(6)))
    lines.append('constexpr int kAppIconSizes[] = { %s };' % ', '.join('int(sizeof(kAppIcon%d))' % i for i in range(6)))
    with open(icons_inc, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('app icons regenerated')

# --- Фирменный фон чата ciraGram (вместо чистого чёрного у ночной темы) ---
code_dir = os.path.join('cira-cloud', 'code')
def code(name):
    return open(os.path.join(code_dir, name), encoding='utf-8').read()

fx_cpp = 'Telegram/SourceFiles/ciragram/effects/ciragram_effects.cpp'
fx_h = 'Telegram/SourceFiles/ciragram/effects/ciragram_effects.h'
edit(fx_cpp, 'constexpr auto kWallpaperFile = "look.wallpaper.file";\n',
     'constexpr auto kWallpaperFile = "look.wallpaper.file";\nconstexpr auto kBrandBackground = "look.cira_background";\n')
edit(fx_cpp, '#include <QtGui/QRadialGradient>\n',
     '#include <QtGui/QRadialGradient>\n#include <QtGui/QLinearGradient>\n#include <QtGui/QTransform>\n#include "ui/style/style_core_scale.h"\n')
edit(fx_cpp, '\tS::Register({\n\t\t.key = QString::fromUtf8(kWallpaperFile),\n\t\t.kind = S::Kind::String,\n\t\t.defaultValue = QString(),\n\t\t.hidden = true,\n\t});\n',
     '\tS::Register({\n\t\t.key = QString::fromUtf8(kWallpaperFile),\n\t\t.kind = S::Kind::String,\n\t\t.defaultValue = QString(),\n\t\t.hidden = true,\n\t});\n' + code('brand_setting.cpp'))
edit(fx_cpp, '\n} // namespace Ciragram::Effects\n',
     code('brand_background.cpp') + '\n} // namespace Ciragram::Effects\n')
edit(fx_h, '[[nodiscard]] bool PaintWallpaper(QPainter &p, QSize fill, QRect clip, bool paused);\n',
     '[[nodiscard]] bool PaintWallpaper(QPainter &p, QSize fill, QRect clip, bool paused);\n'
     '[[nodiscard]] bool PaintBrandBackground(QPainter &p, QSize fill, QRect clip, const QColor &base);\n')
edit(fx_h, 'class QPainter;\n', 'class QPainter;\nclass QColor;\n')
edit('Telegram/SourceFiles/window/section_widget.cpp',
     '\t\tp.fillRect(clip, *background.colorForFill);\n',
     '\t\tif (!Ciragram::Effects::PaintBrandBackground(p, fill, clip, *background.colorForFill)) {\n'
     '\t\t\tp.fillRect(clip, *background.colorForFill);\n'
     '\t\t}\n')
lang_inc = 'Telegram/SourceFiles/ciragram/lang/ciragram_lang_table.inc'
lt, lt_crlf = read_lf(lang_inc)
for ru, en in [
        ('Фирменный фон ciraGram', 'ciraGram background'),
        ('Спокойный узор из знаков ciraGram вместо однотонного фона чата. Работает с однотонными обоями.',
         'A calm pattern of ciraGram marks instead of a plain chat background. Works with solid color wallpapers.')]:
    line = '\t{ "%s", "%s" },\n' % (ru, en)
    if line not in lt:
        lt += line
write_lf(lang_inc, lt, lt_crlf)

# --- Распознавание речи: модель грузится в фоне, интерфейс не замирает при запуске ---
asr = 'Telegram/SourceFiles/ciragram/asr/ciragram_asr.cpp'
edit(asr, '\tbool init() {\n\t\tstd::lock_guard lock(_mutex);\n\t\tif (_initialized) {\n\t\t\treturn _models != nullptr;\n\t\t}\n',
     '\tbool init() {\n\t\tstd::lock_guard lock(_initMutex);\n\t\tif (_initialized) {\n\t\t\treturn ready();\n\t\t}\n')
edit(asr, '\t\t_models = tinyasr_load(\n', '\t\tconst auto models = tinyasr_load(\n')
edit(asr, '\t\tif (!_models) {\n', '\t\tif (!models) {\n')
edit(asr, '\t\t_thread = std::thread([this] { Loop(); });\n',
     '\t\t{\n\t\t\tstd::lock_guard modelsLock(_mutex);\n\t\t\t_models = models;\n\t\t}\n\t\t_thread = std::thread([this] { Loop(); });\n')
edit(asr, '\t~Impl() {\n', '\t~Impl() {\n\t\tstd::lock_guard initLock(_initMutex);\n')
edit(asr, '\tmutable std::mutex _mutex;\n', '\tmutable std::mutex _mutex;\n\tstd::mutex _initMutex;\n')
edit(asr, '\tif (!Engine::Instance().init()) {\n\t\tSettings::SetBool(kKeyEnabled, false);\n\t\treturn;\n\t}\n',
     code('asr_async.cpp'))

# --- Проверка: каждая правка обязана примениться, иначе сборка падает сразу, а не через 5 часов ---
REQUIRED = [
    ('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp', 'внешний бот отключён'),
    ('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp', 'запросы к внешнему боту отключены'),
    ('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp', 'фоновый опрос не нужен'),
    ('Telegram/SourceFiles/ciragram/lang/ciragram_lang.cpp', 'QLocale::system()'),
    ('Telegram/SourceFiles/ciragram/plugins/ciragram_plugins.cpp', 'L"python\\\\"'),
    (fx_cpp, 'bool PaintBrandBackground('),
    (fx_cpp, 'constexpr auto kBrandBackground'),
    (fx_cpp, 'Фирменный фон ciraGram'),
    (fx_cpp, 'QtGui/QLinearGradient'),
    (fx_h, 'PaintBrandBackground'),
    ('Telegram/SourceFiles/window/section_widget.cpp', 'PaintBrandBackground'),
    (asr, 'std::mutex _initMutex;'),
    (asr, 'const auto models = tinyasr_load('),
    (asr, '_models = models;'),
    (asr, 'std::lock_guard initLock(_initMutex);'),
    (asr, 'crl::async([] {'),
    ('Telegram/SourceFiles/boxes/about_box.cpp', 'ciraGram. Основано на Telegram Desktop.'),
    ('Telegram/Resources/winrc/Telegram.rc', 'VALUE "ProductName", "ciraGram"'),
]
missing = [(f, m) for f, m in REQUIRED if not os.path.exists(f) or m not in read_lf(f)[0]]
if missing:
    for f, m in missing:
        print('REQUIRED EDIT MISSING:', f, '->', m)
    sys.exit(1)
print('all required edits present:', len(REQUIRED))
