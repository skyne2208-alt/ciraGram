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

def edit(path, old, new):
    if not os.path.exists(path):
        print('missing', path); return
    s = open(path, encoding='utf-8', errors='surrogateescape', newline='').read()
    if old in s:
        open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s.replace(old, new))
        print('edited', path)

# окно «О программе»: оставляем только Telegram Desktop (его авторство снять нельзя)
ab = 'Telegram/SourceFiles/boxes/about_box.cpp'
if os.path.exists(ab):
    t = open(ab, encoding='utf-8', errors='surrogateescape', newline='').read()
    t2 = re.sub(r'addText\(rpl::single\(\s*TextWithEntities\{ QString::fromUtf8\("ciraGram, автор "\) \}.*?"\)\)\)\);',
                'addText(rpl::single(TextWithEntities{ QString::fromUtf8("ciraGram. Основано на Telegram Desktop.") }));',
                t, count=1, flags=re.S)
    print('about box rewritten' if t2 != t else 'about box: pattern not found')
    open(ab, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(t2)
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
    t = open(mm, encoding='utf-8', errors='surrogateescape', newline='').read()
    t = re.sub(r'links->setMarkedText\(.*?https://t\.me/mokaforum"_q\)\)\);', 'links->setText(QString());', t, count=1, flags=re.S)
    t = re.sub(r'tr::link\(\s*u"ciraGram Desktop"_q,\s*u"https://github\.com/mokagram/mokagram"_q\)',
               'TextWithEntities{ u"ciraGram Desktop"_q }', t, count=1)
    open(mm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(t)

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
    t = open(path, encoding='utf-8', errors='surrogateescape', newline='').read()
    t2, n = re.subn(pattern, repl, t, flags=flags)
    print('sub', path, n)
    if n:
        open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(t2)

sm = 'Telegram/SourceFiles/settings/sections/settings_main.cpp'
sub_file(sm, r'[ \t]*builder\.addButton\(\{\s*\.id = u"main/(?:channel|forum)"_q,.*?\}\);\s*\n', '', re.S)
sub_file(sm, r'(const auto ways = std::vector<Way>\{)\s*.*?\n([ \t]*\};)', r'\1\n\2', re.S)
sub_file('Telegram/SourceFiles/ciragram/music/ciragram_lyrics.cpp',
         r'ciraGram \(https://github\.com/ecronx/mokagram\)', 'ciraGram')
sub_file('Telegram/SourceFiles/ciragram/misc/ciragram_misc.cpp',
         r'https://raw\.githubusercontent\.com/mokagram/mokagram/badges/badges\.json', 'https://cira.invalid/badges.json')
