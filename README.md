# KIV/DS 03

## Popis řešení

### Uzly a ZooKeeper
Uzly používají knihovnu <code>flask-openapi3</code>, což je víceméně nadstavba <code>Flask</code>,
která umožňuje automaticky generovat OpenAPI specifikaci. Uzel ji vystavuje na cestě <code>/openapi</code>, 
json pak na cestě <code>/openapi/openapi.json</code>.

Když se uzel nastartuje, nejprve se zaregistruje u ZooKeeper serveru - kořenový uzel vytvoří nový uzel
v ZooKeeperu pojmenovaný <code>root</code>. Ostatní uzly pak vytváří binární strom. Místo ve stromu hledají
pomocí BFS, kdy hledají první uzel, který nemá dva potomky. Uzly se jmenují <code>child00...N</code>, sekvenci generuje 
ZooKeeper. Uzly kontrolují, jestli již existuje <code>/root</code>, a pokud ne, tak čekají a zkoušejí znovu v 
nekonečné smyčce.

<code>GET</code> požadavky nejprve kontrolují lokální cache, pak volají stejnou metodu rodiče. Adresu rodiče 
získají ze ZooKeeper serveru. Každý uzel, po cestě si klíč a hodnotu ukládají do cache.

<code>PUT</code> požadavek zapíše klíč a hodnotu do lokálního úložiště, pak změnu propaguje směrem ke kořenu.
Všechny uzly po cestě si klíč a hodnotu ukládají do mezipaměti. Pokud klíč již existuje, hodnota je přepsána.
Propagace je asynchronní.

<code>DELETE</code> požadavek odstraní klíč v cache uzlu, pokud existuje. Změna je pak propagována směrem nahoru.
Pokud klíč neexistuje, požadavek není propagován. Nejsem si jistý, jak to zadání zamýšlelo, ale jedná
se o designové rozhodnutí a změna je na dvě řádky kódu.
Propagace je asynchronní.

Při spuštění uzly získávají argumenty ze systémových proměnných, které jsou předány v rámci Vagrantfile.


### CLI klient
CLI klient používá automaticky generovaného OpenAPI klienta. Generátor lze nainstalovat příkazem

<code>pip install openapi-python-client</code>

a klienta lze vygenerovat příkazem

<code>openapi-python-client generate --url *http://[node ip:port]/openapi/openapi.json</code>.

OpenAPI klient se pak nachází ve složce <code>kivds_client</code>, ze které je potřeba package 
<code>kivds_client</code> přesunout do kořenového adresáře projektu.

## Spuštění
### Vagrant
Spuštění uzlů má svá specifika - počet vrstev stromu lze konfigurovat ve Vagrantfile. 
Při lokálním testování byly problémy s připojováním CLI klienta k uzlům, které byly ve vagrant síti.
Kvůli tomu je nastaveno mapování portů uzlů na porty hosta. Porty uzlů začínají na 5001 a jsou inkrementovány.
Uzly ve vagrant síti používají IP adresy, které získávají přes zoonode. Mapování portů bylo provedeno
pouze kvůli přístupu CLI klienta.

Pro spuštění uzlů stačí příkaz <code>vagrant up</code>.

### CLI klient

Klient lze spustit příkazem

<code>python cli.py --server_ip http://[node ip:port]</code>

např. pro připojení ke kořenovému uzlu

<code>python cli.py --server_ip *http://localhost:5001*</code>

Klient podporuje příkazy
* <code>get [key]</code>
* <code>delete [key]</code>
* <code>put [key] [value]</code>
* <code>getall</code> - vrátí všechny klíče a hodnoty uložené v uzlu 
* <code>exit</code>

Klient validuje vstup a vypisuje nápovědu při nesprávném počtu argumentů.

## Zajištění konzistence
Co se týče <code>GET</code> operace, konzistence je zajištěna. Problémové jsou operace <code>PUT</code> 
a <code>DELETE</code>.

Z pohledu rychlosti konvergence vidím dvě možnosti - buďto okamžitě synchronizovat každou změnu, nebo provádět
periodické aktualizace.

Pokud by se propagovala každá změna, za akceptovalné řešení bych považoval propagaci směrem ke kořenovému uzlu,
kde by ale každý uzel po cestě propagoval změny do každého potomka až na toho, od kterého změna přišla. Protože
jsou uzly organizovány v binárním stomu, není potřeba řešit cyklení. To platí pro operace <code>PUT</code> a 
<code>DELETE</code>. Operace <code>GET</code> není z pohledu konzistence problematická.

Pokud by nebyla vyžadována okamžitá konzistence, napadají mě dvě možnosti - buďto bude aktualizaci dat periodicky
zajišťovat kořenový uzel, nebo dotazované uzly.

Pokud by aktualizaci zajišťoval kořenový uzel, princip by byl takový, že by periodicky poslal aktuální data
všem pomotků, které by se rekurzivně propagovaly směrem dolů ve stromu. Použitelnost takového přístupu
závisí na celkovém objemu dat, distribuci požadavků mezi uzly a distribuci požadavků na data mezi uzly.
Mohlo by dojít k situaci, kdy by se velké objemy dat propagovaly do uzlů, které na ně nejsou dotazovány.

Pokud by se o aktualizace staraly samotné uzly, tak základní framework by fungoval tak, jako teď - propagace změn
směrem ke kořenovému uzlu a cachování změn po cestě. Každý uzel by si ale navíc pro každý klíč udržoval 
timestamp poslední aktualizace. Když by byl dotázán na jeho hodnotu (<code>GET</code>), porovnal by s klíčem
spojenou časovou značku, a pokud by od poslední aktualizace uplynul daný čas, místo toho, aby vrátil hodnotu v cache,
poslal by <code>GET</code> rodiči. Tento proces by se opakoval i ve vyšších vrstvách stromu, takže
pokud by rodič měl dostatečně aktuální hodnotu, nemusel by požadavek dojít až ke kořenovému uzlu. Při návratu 
<code>GET</code> požadavku zpět k dotázanému uzlu by se v uzlech po cestě také hodnoty pro daný klíč aktualizovaly.


