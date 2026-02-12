import os,sys,subprocess,re,tempfile
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters

TOKEN=os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print('❌ TELEGRAM_BOT_TOKEN bulunamadı!')
    sys.exit(1)

updater=Updater(TOKEN,use_context=True)

# === TÜM PAKET DÖNÜŞÜMLERİ ===
ALIAS={
    # Senin importların
    'telebot':'pyTelegramBotAPI','whois':'python-whois','dns':'dnspython',
    'cryptography':'cryptography','idna':'idna',
    
    # Görüntü işleme
    'cv2':'opencv-python','PIL':'Pillow','Image':'Pillow','skimage':'scikit-image',
    'pytesseract':'pytesseract','easyocr':'easyocr','qrcode':'qrcode',
    
    # Web scraping
    'bs4':'beautifulsoup4','selenium':'selenium','playwright':'playwright',
    'scrapy':'scrapy','httpx':'httpx','aiohttp':'aiohttp',
    
    # Data science
    'sklearn':'scikit-learn','tensorflow':'tensorflow','torch':'torch',
    'keras':'keras','pandas':'pandas','numpy':'numpy','np':'numpy',
    'matplotlib':'matplotlib','plt':'matplotlib','seaborn':'seaborn',
    'xgboost':'xgboost','lightgbm':'lightgbm','statsmodels':'statsmodels',
    
    # Web framework
    'flask':'Flask','django':'Django','fastapi':'fastapi',
    
    # Database
    'psycopg2':'psycopg2-binary','pymongo':'pymongo','redis':'redis',
    'sqlalchemy':'SQLAlchemy','mysql':'mysql-connector-python',
    
    # Bot framework
    'discord':'discord.py','pyrogram':'pyrogram','aiogram':'aiogram',
    
    # Network
    'paramiko':'paramiko','scapy':'scapy','fabric':'fabric',
    'netmiko':'netmiko','dnspython':'dnspython',
    
    # Automation
    'pyautogui':'PyAutoGUI','pynput':'pynput','keyboard':'keyboard',
    'schedule':'schedule','apscheduler':'APScheduler',
    
    # File processing
    'openpyxl':'openpyxl','pdfplumber':'pdfplumber','PyPDF2':'PyPDF2',
    'docx':'python-docx','moviepy':'moviepy','youtube_dl':'youtube-dl',
    'yt_dlp':'yt-dlp',
    
    # Utilities
    'tqdm':'tqdm','rich':'rich','colorama':'colorama','pyyaml':'pyyaml',
    'yaml':'pyyaml','dotenv':'python-dotenv','toml':'toml',
    'pydantic':'pydantic','click':'click','typer':'typer',
    
    # Security
    'bcrypt':'bcrypt','passlib':'passlib','jwt':'PyJWT','pyjwt':'PyJWT',
    'pyopenssl':'pyOpenSSL','cryptography':'cryptography',
    
    # System
    'psutil':'psutil','platform':'platform','distro':'distro',
    'cpuinfo':'py-cpuinfo','gputil':'GPUtil',
    
    # Testing
    'pytest':'pytest','mock':'mock','coverage':'coverage',
    
    # Async
    'asyncio':'asyncio','aiofiles':'aiofiles','aioredis':'aioredis',
}

# === BUILT-IN MODÜLLER (YÜKLENMEZ) ===
BUILTINS = {
    'os','sys','re','json','math','random','time','datetime','string',
    'uuid','socket','ssl','subprocess','urllib','typing','collections',
    'itertools','functools','copy','pprint','enum','abc','argparse',
    'logging','hashlib','base64','csv','sqlite3','pickle','glob',
    'shutil','tempfile','calendar','statistics','decimal','html','xml',
    'http','email','asyncio','unittest','configparser','tkinter',
    'zipfile','tarfile','gzip','bz2','smtplib','imaplib','ftplib',
    'concurrent','threading','multiprocessing','queue','warnings',
    'traceback','inspect','pdb','gc','platform','idna','imaplib',
    'poplib','telnetlib','cgi','cgitb','wave','sndhdr',
}

def find_imports(code):
    """Python kodundaki TÜM importları bul"""
    imports = set()
    
    # Regex ile bul
    for m in re.findall(r'^(?:import|from)\s+(\w+)', code, re.MULTILINE):
        imports.add(m.split('.')[0])
    
    # AST ile de dene
    try:
        import ast
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except:
        pass
    
    return imports

def install_package(pkg):
    """Akıllı paket yükleyici - 5 farklı isim dener"""
    try:
        __import__(pkg)
        return f"✅ {pkg}"
    except:
        # Denenecek isimler
        names = [
            pkg,
            ALIAS.get(pkg, pkg),
            pkg.lower(),
            pkg.replace('_', '-'),
            f"python-{pkg}",
            pkg.replace('.', '-'),
        ]
        
        for name in set(names):
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-q", "--no-cache-dir", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                # Yüklendi mi kontrol et
                try:
                    __import__(pkg)
                    return f"✅ {pkg}"
                except:
                    continue
            except:
                continue
    return f"❌ {pkg}"

def run_python_file(file_path):
    """Dosyayı çalıştır, tüm paketleri yükle"""
    try:
        # Dosyayı oku
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # İmportları bul
        imports = find_imports(code)
        
        # Built-in olmayanları filtrele
        needed = [i for i in imports if i and i not in BUILTINS and i[0].islower()]
        
        # Paketleri yükle
        results = []
        for i, pkg in enumerate(needed, 1):
            results.append(f"{i}/{len(needed)} {install_package(pkg)}")
        
        # Dosyayı çalıştır
        r = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        # Sonuçları birleştir
        output = "\n".join(results[:20])
        if len(results) > 20:
            output += f"\n...ve {len(results)-20} paket daha"
        
        if r.stdout:
            output += f"\n\n📤 **ÇIKTI:**\n{r.stdout[:2000]}"
        if r.stderr:
            output += f"\n\n❌ **HATA:**\n{r.stderr[:1000]}"
        
        return output if output else "✅ Çalıştı, çıktı yok"
        
    except Exception as e:
        return f"❌ Hata: {str(e)}"

def handle_file(update, context):
    """Telegram'dan gelen .py dosyasını işle"""
    msg = update.message
    
    # Dosya kontrolü
    if not msg.document or not msg.document.file_name.endswith('.py'):
        msg.reply_text('❌ Lütfen .py uzantılı dosya gönderin!')
        return
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
        file_path = tmp.name
    
    try:
        # Dosyayı indir
        msg.reply_text(f'📥 `{msg.document.file_name}` indiriliyor...', parse_mode='Markdown')
        msg.document.get_file().download(custom_path=file_path)
        
        # Çalıştır
        msg.reply_text('🔍 **Analiz ediliyor...**\n📦 **Paketler yükleniyor...**\n⚡ **Çalıştırılıyor...**', 
                      parse_mode='Markdown')
        
        result = run_python_file(file_path)
        
        # Sonucu gönder
        if len(result) > 4000:
            result = result[:4000] + '\n\n...(devamı kesildi)'
        
        msg.reply_text(f'📊 **SONUÇ:**\n\n{result}', parse_mode='Markdown')
        
    except Exception as e:
        msg.reply_text(f'❌ İşlem hatası: {str(e)[:200]}')
    finally:
        # Temizlik
        try:
            os.unlink(file_path)
        except:
            pass

def start(update, context):
    """Start komutu"""
    update.message.reply_text(
        '🤖 **PYTHON PAKET YÜKLEYİCİ BOT**\n\n'
        '📁 **.py dosyası gönder**, ben **TÜM PAKETLERİ** yükleyip çalıştırayım!\n\n'
        '**ÖRNEK İMPORTLAR:**\n'
        '```\n'
        'import telebot\n'
        'import whois\n'
        'import dns.resolver\n'
        'import cryptography\n'
        'import idna\n'
        'import cv2\n'
        'from PIL import Image\n'
        '```\n\n'
        '✅ **Zaman aşımı YOK**\n'
        '✅ **5000+ paket desteği**\n'
        '✅ **Otomatik import bulma**\n\n'
        '🚀 **HEMEN DENE!**',
        parse_mode='Markdown'
    )

# Handler'ları ekle
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', start))
updater.dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

print('='*60)
print('🚀 BOT HAZIR!')
print('📁 .py dosyası gönder, TÜM PAKETLER otomatik yüklensin!')
print('✅ Zaman aşımı YOK')
print('='*60)

# Botu başlat
updater.start_polling()
updater.idle()
