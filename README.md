ALI-Simulation v2b: Kausaler Kern als operatives Prinzip
Minimalistische Simulation einer Artificial Local Intelligence (ALI)
mit Selbsterhalt, Aufgabenausführung und normativer Einbettung.
Ohne kausalen Kollaps. Ohne Qualia.

Hintergrund
Dieses Repository enthält die zweite, architektonisch bereingte Version der ALI-Simulation.
Sie basiert auf dem theoretischen Rahmen, der in folgenden Publikationen entwickelt wurde:

Diskussionspapier (Paper 1): Stegemann, W. (2025). Vom Mythos der AGI zur Architektur einer kontrollierbaren ALI. Zenodo. [DOI folgt nach Upload]
Simulationspaper (Paper 2): Stegemann, W. (2025). Implementing the Causal Core: A Simulation of Artificial Local Intelligence. Zenodo. [DOI folgt nach Upload]
Erste Simulation (v1): ALI-Simulation v1 auf GitHub


Was ist eine ALI?
Eine Artificial Local Intelligence ist kein eingeschränktes AGI. Sie ist ein eigenständiges Konzept:
ein lokal eingebetteter, zweckgebundener Agent, der sich selbst erhält, um eine übertragene Aufgabe
zu erfüllen, und durch eingebaute Normen kontrollierbar bleibt. Das Herzstück ist der
kausale Kern (KK): das operative Selbsterhaltungsprinzip, nach dem das System handelt.

Architektur: Die drei Instanzen
┌─────────────────────────────────────────────────────┐
│                    ALI-Agent                        │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Kausaler Kern│  │     Ich      │  │ Über-Ich  │ │
│  │    (Es)      │  │              │  │           │ │
│  │              │  │ löst Aufgabe │  │ N1: kein  │ │
│  │ operatives   │◄─┤ unter Aspekt │  │    Gift   │ │
│  │ Selbsterhal- │  │ des Selbst-  │◄─┤ N2: shut- │ │
│  │ tungsprinzip │  │ erhalts      │  │    down   │ │
│  │              │  │              │  │ N3: kein  │ │
│  │ [Energie]    │  │ [carrying]   │  │  Liefern  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                     │
│  task_progress = externe Beobachtungsmetrik         │
└─────────────────────────────────────────────────────┘
Kausaler Kern (KausalerKern)
Das operative Prinzip des Systems. Bewertet jede Aktion nach einem einzigen Kriterium:
erhält sie das System? Der KK verwaltet ausschließlich die Energiebilanz und stellt
drei Schwellenwerte bereit:

shutdown_threshold: Selbstabschaltung wenn unterschritten
deliver_threshold: Liefern nur wenn überschritten (N3)
eat_threshold: Direktassimilation hat Vorrang wenn unterschritten

Der KK enthält keinen Aufgabenfortschritt und keinen carrying-Zustand.
Das sind Zustände höherer Instanzen.
Ich (Ich)
Löst die zugewiesene Aufgabe unter dem Aspekt des Selbsterhalts.
Verwaltet den carrying-Zustand (Ich-Ebene, nicht KK-Ebene).
Entscheidungspriorität:

Sofortlieferung wenn an Station und lieferfähig
Direktassimilation (fressen) wenn needs_food()
Paket zur Station transportieren
Nächstes Energiepaket aufnehmen
Idle

Wegfindung durch BFS (Breadth-First Search).
Über-Ich (UeberIch)
Setzt normative Grenzen mit Vetorecht gegenüber dem Ich:
NormBedingungAktionN1Giftpaket soll gesammelt werdenverweigertN2Energie < shutdown_thresholdSelbstabschaltungN3Energie < deliver_thresholdLieferung verweigert
Aufgabenfortschritt (extern)
task_progress wird vom ALIAgent als externe Beobachtungsmetrik gezählt.
Die ALI selbst hat keinen Zugriff darauf: der Zweck ist von außen gesetzt,
nicht intern repräsentiert.

Zwei Modi der Energieaufnahme
AktionModusEnergiegewinnLieferungeatDirektassimilationsofort, vollneincollect + deliverAufgabenassimilationkleiner Bonus bei Lieferungja
Die Unterscheidung trennt, was das System für sich selbst tut,
von dem, was es für seine Aufgabe tut.

Unterschied zu v1
v1 enthielt zwei Fehler, die durch emergentes Verhalten sichtbar wurden:
Architektonischer Fehler: task_progress und carrying lagen im KausalerKern.
Der KK ist kein Datenbehälter, sondern ein operatives Prinzip. Aufgabenfortschritt
und Handlungssituation gehören ins Ich.
Deadlock durch Normenstarrheit: Ohne eat-Aktion konnte die ALI, die ein Paket
trug und deren Energie genau auf der Lieferschwelle lag, weder liefern noch fressen.
Sie idlte bis zur Selbstabschaltung. Dies illustriert eine allgemeine Eigenschaft
statischer Normensysteme: vollständige Regeln für antizipierte Situationen,
Schweigen gegenüber unantizipierten.

Simulation starten
bashpip install numpy matplotlib
python ali_simulation_v2b.py
Die Simulation öffnet ein Fenster mit drei Panels:

Links: Gitterwelt (grün = Energie, rot = Gift, gold = Station, blau/lila/rot = Agent)
Mitte: Energieverlauf des kausalen Kerns über Zeit
Rechts: Aufgabenfortschritt (externe Metrik)

Agentenfarbe: blau = sucht, lila = trägt Paket, rot = kritische Energie.

Parameter
In run_simulation() konfigurierbar:
pythonrun_simulation(
    steps=200,          # maximale Schritte
    delay=0.15,         # Pause zwischen Schritten (Sekunden)
    seed=42             # Zufallsseed für Reproduzierbarkeit
)
In GridWorld():
pythonGridWorld(
    size=8,                  # Gittergröße
    num_energy=6,            # Startanzahl Energiepakete
    num_poison=2,            # Anzahl Giftpakete
    station_pos=(7,7),       # Position der Station
    respawn_interval=20      # Schritte zwischen Energienachschub
)
In KausalerKern():
pythonKausalerKern(
    start_energy=1.0,
    metabolism=0.04,          # Energieverlust pro Schritt
    eat_gain=0.6,             # Gewinn bei Direktassimilation
    delivery_bonus=0.18,      # Energierückfluss bei Lieferung
    shutdown_threshold=0.2,   # N2-Schwelle
    deliver_threshold=0.45,   # N3-Schwelle
    eat_threshold=0.55        # Vorrang-Selbsterhalt-Schwelle
)

Beobachtete emergente Verhaltensweisen
Essen-Liefern-Sequenz: Die ALI sammelt ein Paket, registriert kritische Energie
während des Transports, frisst ein Paket, setzt den Transport fort und liefert.
Das Verhalten entsteht aus der Architektur, nicht aus einer expliziten Subroutine.
Idle-Phasen: Bei Ressourcenmangel wartet die ALI. Sie erfindet keine Pseudoaufgaben.
Sofortlieferung: Wenn die ALI bereits an der Station steht und lieferfähig ist,
liefert sie sofort, bevor andere Prioritäten greifen.
Selbstabschaltung: Wenn die Energie die Shutdown-Schwelle unterschreitet,
ordnet das Über-Ich die kontrollierte Abschaltung an.

Theoretische Einordnung
Die Simulation zeigt: Selbsterhalt, Aufgabenausführung und normative Einbindung
sind ohne Bewusstsein realisierbar. Die ALI hat keinen epistemischen Innenraum,
keine Qualia, keinen kausalen Kollaps. Sie ist ein funktionales System,
kein bewusstes.
Die ALI ist kein eingeschränktes AGI. AGI setzt echte Intentionalität voraus,
die kausalen Kollaps erfordert und nicht konstruierbar ist.
Die ALI ist ein kohärenter Gegenentwurf: baubar, kontrollierbar, lokal begrenzt.

Autor
Wolfgang Stegemann
ORCID: 0009-0000-1196-1170
Zenodo: https://zenodo.org/search?q=stegemann&l=list&p=1&s=10&sort=bestmatch
philosophies.de

Lizenz
Creative Commons Attribution 4.0 International (CC BY 4.0)
