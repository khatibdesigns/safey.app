#!/usr/bin/env python3
"""Build translated homepages (/es/, /pt/, /fr/, ...) from index.html.

The English page is the layout source of truth: CSS, nav, footer and the
carousel / lock-demo / crypt scripts are reused verbatim, only text is swapped
and <main> is rebuilt from the template below. Every page lists every other
language in hreflang, and the same set is written back into / and /ar/.

    python3 new-home-locale.py          # writes <lang>/index.html for all locales
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).parent
BASE = (ROOT / "index.html").read_text()
STORE = "https://apps.apple.com/app/id1189852939"

# Every language the site serves, for hreflang + the footer switcher.
ALL = {"en": ("/", "English"), "ar": ("/ar/", "العربية"), "es": ("/es/", "Español"),
       "pt": ("/pt/", "Português"), "fr": ("/fr/", "Français"), "de": ("/de/", "Deutsch"),
       "it": ("/it/", "Italiano"), "tr": ("/tr/", "Türkçe"), "id": ("/id/", "Bahasa Indonesia")}

LOCK = '<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M8 11V8a4 4 0 018 0v3" stroke="currentColor" stroke-width="1.7"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHIP_ICONS = [
    '<svg viewBox="0 0 24 24" fill="none"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" stroke="currentColor" stroke-width="1.6"/><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><path d="M12 15a2 2 0 100-4 2 2 0 000 4z" stroke="currentColor" stroke-width="1.6"/><path d="M5 11V8a7 7 0 0114 0v3" stroke="currentColor" stroke-width="1.6"/><rect x="4" y="11" width="16" height="10" rx="2.5" stroke="currentColor" stroke-width="1.6"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
]
FEAT_ICONS = [
    '<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="5" width="16" height="14" rx="2.5" stroke="currentColor" stroke-width="1.7"/><circle cx="9" cy="10" r="1.6" stroke="currentColor" stroke-width="1.5"/><path d="M5 17l4.5-4 3 2.5L16 11l3 3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="9" width="12" height="12" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M8 9V7a4 4 0 018 0" stroke="currentColor" stroke-width="1.7"/><circle cx="18" cy="7" r="3" stroke="currentColor" stroke-width="1.7"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="6" width="18" height="12" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M3 10h18" stroke="currentColor" stroke-width="1.7"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="4" width="14" height="16" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M9 9h6M9 13h6M9 17h3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="10" r="4" stroke="currentColor" stroke-width="1.7"/><path d="M4 20c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><path d="M6 4h7l5 5v11a1 1 0 01-1 1H6a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" stroke-width="1.7"/><path d="M13 4v5h5" stroke="currentColor" stroke-width="1.7"/></svg>',
]
SHOTS = ["photo-1506905925346-21bda4d32df4", "photo-1441974231531-c6227db76b6e",
         "photo-1470071459604-3b5ec3a7fe05", "photo-1501785888041-af3ef285b470"]

T = {
"es": dict(
  title="Safey: bóveda privada de fotos y contraseñas para iPhone",
  desc="Safey es una bóveda privada para iPhone: oculta fotos y videos tras Face ID y guarda contraseñas, tarjetas y notas cifradas en tu dispositivo con AES-256.",
  keywords="ocultar fotos iphone, bóveda de fotos, app para ocultar fotos, álbum secreto, gestor de contraseñas, app privada, bloquear fotos iphone",
  nav_small="Gratis en", cta_small="Descárgala en", how_btn="Cómo funciona",
  eyebrow="iOS · Face ID · AES-256", h1=("La bóveda para todo lo que prefieres ", "mantener oculto", "."),
  lede="Saca tus fotos y videos privados del carrete y guarda contraseñas, tarjetas, notas y archivos en un solo lugar que solo se abre con tu cara.",
  chips=["Contraseñas cifradas", "Bloqueo con Face ID", "Se bloquea al instante"],
  alts=["Pantalla principal de la bóveda de Safey", "Generador de contraseñas seguras de Safey", "Pantalla de bloqueo de Safey con Face ID"],
  caps=["Toda tu bóveda, a un toque", "Contraseñas seguras en un toque", "Siempre tras Face ID"],
  how_eyebrow="El problema del carrete", how_h2="Tu álbum \"Oculto\" no está realmente oculto.",
  how_p="Cualquiera que desbloquee tu teléfono puede abrirlo. Safey lleva tus fotos y videos privados a una bóveda que solo se abre para ti, así puedes prestar el teléfono sin preocuparte.",
  exposed="estado: <b>expuesto</b> · cualquiera puede verlas", secured="estado: <b>protegido</b> · bloqueado con Face ID",
  lock_btn="Bloquear la bóveda", unlock_btn="Desbloquear",
  feat_eyebrow="Una bóveda, no cinco apps", feat_h2="Todo lo privado, en un solo lugar.",
  feat_p="La mayoría de apps solo ocultan fotos o solo guardan contraseñas. Safey lo guarda todo tras el mismo bloqueo.",
  feats=[("Fotos y videos ocultos", "Fuera del carrete, en un álbum con Face ID que nadie más puede abrir."),
         ("Contraseñas y accesos", "Todos tus accesos, con generador de contraseñas fuertes."),
         ("Tarjetas, PIN y CVC", "Datos de pago cifrados, visibles solo tras verificar tu cara."),
         ("Notas seguras", "Códigos de recuperación, claves wifi, datos del pasaporte."),
         ("Alertas de intrusión", "Cada desbloqueo fallido toma en secreto una foto de quien lo intenta."),
         ("Archivos y documentos", "Identificaciones, certificados y PDF dentro de la bóveda.")],
  sec_eyebrow="Cómo funciona el cifrado", sec_h2="Cifrado antes de salir de tu teléfono.",
  sec_p="Contraseñas, tarjetas, CVC, PIN y notas se cifran con AES-256 en tu iPhone. La clave vive en el llavero de tu dispositivo y nunca sale de él, así que nadie puede leerlos. Ni un atacante, ni nosotros.",
  sec_points=["Cifrado en el dispositivo, antes de sincronizar", "La clave nunca sale de tu llavero", "Fotos y videos ocultos tras Face ID"],
  sec_tag="cifrado en el dispositivo", note_plain="Código de la caja fuerte: 4471",
  price_eyebrow="Gratis para empezar", price_h2="Tu bóveda completa, gratis.",
  price_p="Safey Pro añade protección y espacio, y los primeros 7 días son gratis.",
  tiers=[("GRATIS", "Gratis", "para siempre", "Fotos y videos tras Face ID, más contraseñas, tarjetas y notas cifradas con AES-256.", "500 MB incluidos"),
         ("PRO", "50 GB", "desde $2.99/mes", "Mira la cara de quien intentó entrar, usa un código señuelo y guarda mucho más.", "7 días gratis"),
         ("PRO MAX", "200 GB", "desde $5.99/mes", "Todo lo de Pro con el máximo espacio para tus archivos privados.", "7 días gratis")],
  faq_eyebrow="Bueno saberlo", faq_h2="Preguntas frecuentes.",
  faqs=[("¿Cómo oculto fotos y videos en el iPhone?", "Abre la bóveda de fotos de Safey e importa las fotos y videos que quieras ocultar. Pasan a un álbum bloqueado con Face ID y puedes borrarlos del carrete para que nadie los vea al revisar tus fotos."),
        ("¿Safey es realmente privado?", "Las contraseñas, números de tarjeta, CVC, PIN y notas se cifran con AES-256 en tu iPhone antes de subirse, y la clave nunca sale del llavero de tu dispositivo. Las fotos y videos quedan bloqueados tras Face ID dentro de la bóveda, aunque todavía no se cifran en reposo. Preferimos decírtelo claramente."),
        ("¿Qué pasa si alguien intenta abrir mi bóveda?", "Cada intento fallido toma en silencio una foto con la cámara frontal y registra la hora. Con Safey Pro ves la foto y el historial completo."),
        ("¿Qué pasa si pierdo el teléfono?", "La bóveda está protegida con Face ID, Touch ID o el código del dispositivo. Tus datos se sincronizan de forma privada para que puedas restaurarlos en un iPhone nuevo iniciando sesión."),
        ("¿Safey es gratis?", "Sí. Safey es gratis para descargar y usar con 500 MB. Safey Pro es opcional, incluye 7 días de prueba gratis y después se renueva al precio mostrado en la app salvo que lo canceles.")],
  guides_eyebrow="Guías", guides_h2="Privacidad y almacenamiento, explicados (en inglés).", all_guides="Todas las guías →",
  final_h2="Que siga siendo tuyo.", final_p="Descarga Safey y protege tus fotos privadas, contraseñas y archivos, gratis en el App Store.",
  foot_by="una bóveda privada de", foot_guides="Guías", foot_privacy="Privacidad", foot_terms="Términos",
),
"pt": dict(
  title="Safey: cofre privado de fotos e senhas para iPhone",
  desc="Safey é um cofre privado para iPhone: esconda fotos e vídeos com Face ID e guarde senhas, cartões e notas criptografados no aparelho com AES-256.",
  keywords="esconder fotos iphone, cofre de fotos, app para esconder fotos, álbum secreto, gerenciador de senhas, app privado, trancar fotos iphone",
  nav_small="Grátis na", cta_small="Baixe na", how_btn="Como funciona",
  eyebrow="iOS · Face ID · AES-256", h1=("O cofre para tudo o que você prefere ", "manter escondido", "."),
  lede="Tire suas fotos e vídeos privados do rolo da câmera e guarde senhas, cartões, notas e arquivos em um só lugar que só abre com o seu rosto.",
  chips=["Senhas criptografadas", "Bloqueio com Face ID", "Tranca na hora"],
  alts=["Tela inicial do cofre Safey", "Gerador de senhas fortes do Safey", "Tela de bloqueio do Safey com Face ID"],
  caps=["Seu cofre inteiro, a um toque", "Senhas fortes em um toque", "Sempre protegido pelo Face ID"],
  how_eyebrow="O problema do rolo da câmera", how_h2="Seu álbum \"Oculto\" não está realmente oculto.",
  how_p="Qualquer pessoa que desbloqueie seu celular consegue abrir. O Safey leva suas fotos e vídeos privados para um cofre que só abre para você, então você pode emprestar o celular sem preocupação.",
  exposed="status: <b>exposto</b> · qualquer um vê", secured="status: <b>protegido</b> · trancado com Face ID",
  lock_btn="Trancar o cofre", unlock_btn="Destrancar",
  feat_eyebrow="Um cofre, não cinco apps", feat_h2="Tudo que é privado, em um só lugar.",
  feat_p="A maioria dos apps esconde só fotos ou guarda só senhas. O Safey guarda tudo atrás do mesmo bloqueio.",
  feats=[("Fotos e vídeos ocultos", "Fora do rolo da câmera, em um álbum com Face ID que ninguém mais abre."),
         ("Senhas e logins", "Todos os seus acessos, com gerador de senhas fortes."),
         ("Cartões, PINs e CVCs", "Dados de pagamento criptografados, revelados só após verificar seu rosto."),
         ("Notas seguras", "Códigos de recuperação, senhas de wi-fi, dados do passaporte."),
         ("Alertas de invasão", "Cada desbloqueio errado tira, em segredo, uma foto de quem tentou."),
         ("Arquivos e documentos", "Documentos de identidade, certificados e PDFs dentro do cofre.")],
  sec_eyebrow="Como funciona a criptografia", sec_h2="Criptografado antes de sair do seu celular.",
  sec_p="Senhas, cartões, CVCs, PINs e notas são criptografados com AES-256 no seu iPhone. A chave fica nas Chaves do aparelho e nunca sai dele, então ninguém consegue ler. Nem um invasor, nem nós.",
  sec_points=["Criptografado no aparelho, antes de sincronizar", "A chave nunca sai das suas Chaves", "Fotos e vídeos ocultos atrás do Face ID"],
  sec_tag="criptografado no aparelho", note_plain="Senha do cofre de casa: 4471",
  price_eyebrow="Grátis para começar", price_h2="Seu cofre completo, grátis.",
  price_p="O Safey Pro adiciona proteção e espaço, e os primeiros 7 dias são grátis.",
  tiers=[("GRÁTIS", "Grátis", "para sempre", "Fotos e vídeos com Face ID, além de senhas, cartões e notas criptografados com AES-256.", "500 MB inclusos"),
         ("PRO", "50 GB", "a partir de US$2,99/mês", "Veja o rosto de quem tentou entrar, use um código isca e guarde muito mais.", "7 dias grátis"),
         ("PRO MAX", "200 GB", "a partir de US$5,99/mês", "Tudo do Pro com o máximo de espaço para seus arquivos privados.", "7 dias grátis")],
  faq_eyebrow="Bom saber", faq_h2="Perguntas frequentes.",
  faqs=[("Como esconder fotos e vídeos no iPhone?", "Abra o cofre de fotos do Safey e importe as fotos e vídeos que quer esconder. Eles vão para um álbum trancado com Face ID e você pode apagá-los do rolo da câmera para que ninguém os veja."),
        ("O Safey é realmente privado?", "Senhas, números de cartão, CVCs, PINs e notas são criptografados com AES-256 no seu iPhone antes do envio, e a chave nunca sai das Chaves do aparelho. Fotos e vídeos ficam trancados atrás do Face ID no cofre, mas ainda não são criptografados em repouso. Preferimos dizer isso com clareza."),
        ("O que acontece se alguém tentar abrir meu cofre?", "Cada tentativa errada tira, em silêncio, uma foto com a câmera frontal e registra o horário. Com o Safey Pro você vê a foto e o histórico completo."),
        ("E se eu perder o celular?", "O cofre é protegido por Face ID, Touch ID ou pelo código do aparelho. Seus dados sincronizam de forma privada para você restaurar tudo em um iPhone novo fazendo login."),
        ("O Safey é grátis?", "Sim. O Safey é grátis para baixar e usar com 500 MB. O Safey Pro é opcional, tem 7 dias grátis e depois renova pelo preço mostrado no app, a menos que você cancele.")],
  guides_eyebrow="Guias", guides_h2="Privacidade e armazenamento, explicados (em inglês).", all_guides="Todos os guias →",
  final_h2="Mantenha só seu.", final_p="Baixe o Safey e proteja suas fotos privadas, senhas e arquivos, grátis na App Store.",
  foot_by="um cofre privado da", foot_guides="Guias", foot_privacy="Privacidade", foot_terms="Termos",
),
"fr": dict(
  title="Safey : coffre-fort photos et mots de passe pour iPhone",
  desc="Safey est un coffre-fort privé pour iPhone : cachez photos et vidéos derrière Face ID et gardez mots de passe, cartes et notes chiffrés sur l'appareil en AES-256.",
  keywords="cacher photos iphone, coffre-fort photo, application pour cacher des photos, album secret, gestionnaire de mots de passe, app privée",
  nav_small="Gratuit sur", cta_small="Télécharger dans", how_btn="Voir comment ça marche",
  eyebrow="iOS · Face ID · AES-256", h1=("Le coffre-fort pour tout ce que vous préférez ", "garder caché", "."),
  lede="Sortez vos photos et vidéos privées de la pellicule et gardez mots de passe, cartes, notes et fichiers au même endroit, qui ne s'ouvre qu'avec votre visage.",
  chips=["Mots de passe chiffrés", "Verrou Face ID", "Verrouillage instantané"],
  alts=["Écran d'accueil du coffre Safey", "Générateur de mots de passe forts de Safey", "Écran de verrouillage Face ID de Safey"],
  caps=["Tout votre coffre, en un geste", "Des mots de passe forts en un geste", "Toujours derrière Face ID"],
  how_eyebrow="Le problème de la pellicule", how_h2="Votre album « Masqués » n'est pas vraiment caché.",
  how_p="Quiconque déverrouille votre téléphone peut l'ouvrir. Safey déplace vos photos et vidéos privées dans un coffre qui ne s'ouvre que pour vous : prêtez votre téléphone sans arrière-pensée.",
  exposed="état : <b>exposé</b> · tout le monde peut les voir", secured="état : <b>protégé</b> · verrouillé par Face ID",
  lock_btn="Verrouiller le coffre", unlock_btn="Déverrouiller",
  feat_eyebrow="Un coffre, pas cinq apps", feat_h2="Tout votre privé, au même endroit.",
  feat_p="La plupart des apps ne cachent que les photos, ou ne gardent que les mots de passe. Safey garde tout derrière le même verrou.",
  feats=[("Photos et vidéos cachées", "Hors de la pellicule, dans un album Face ID que personne d'autre n'ouvre."),
         ("Mots de passe et identifiants", "Tous vos accès, avec un générateur de mots de passe forts."),
         ("Cartes, PIN et CVC", "Données bancaires chiffrées, affichées seulement après vérification du visage."),
         ("Notes sécurisées", "Codes de récupération, mots de passe wifi, données de passeport."),
         ("Alertes d'intrusion", "Chaque déverrouillage raté photographie discrètement la personne qui essaie."),
         ("Fichiers et documents", "Pièces d'identité, certificats et PDF dans le coffre.")],
  sec_eyebrow="Comment fonctionne le chiffrement", sec_h2="Chiffré avant de quitter votre téléphone.",
  sec_p="Mots de passe, cartes, CVC, codes PIN et notes sont chiffrés en AES-256 sur votre iPhone. La clé reste dans le trousseau de l'appareil et ne le quitte jamais : personne ne peut les lire. Ni un pirate, ni nous.",
  sec_points=["Chiffré sur l'appareil, avant toute synchro", "La clé ne quitte jamais votre trousseau", "Photos et vidéos cachées derrière Face ID"],
  sec_tag="chiffré sur l'appareil", note_plain="Code du coffre de l'appart : 4471",
  price_eyebrow="Gratuit pour commencer", price_h2="Votre coffre complet, gratuit.",
  price_p="Safey Pro ajoute protection et espace, et les 7 premiers jours sont gratuits.",
  tiers=[("GRATUIT", "Gratuit", "pour toujours", "Photos et vidéos derrière Face ID, plus mots de passe, cartes et notes chiffrés en AES-256.", "500 Mo inclus"),
         ("PRO", "50 Go", "dès 2,99 $/mois", "Voyez le visage de qui a essayé d'entrer, utilisez un code leurre et gardez bien plus.", "7 jours gratuits"),
         ("PRO MAX", "200 Go", "dès 5,99 $/mois", "Tout Pro, avec le maximum d'espace pour vos fichiers privés.", "7 jours gratuits")],
  faq_eyebrow="Bon à savoir", faq_h2="Vos questions, nos réponses.",
  faqs=[("Comment cacher des photos et vidéos sur iPhone ?", "Ouvrez le coffre photo de Safey et importez les photos et vidéos à cacher. Elles passent dans un album verrouillé par Face ID, et vous pouvez les supprimer de la pellicule pour que personne ne les voie."),
        ("Safey est-il vraiment privé ?", "Mots de passe, numéros de carte, CVC, codes PIN et notes sont chiffrés en AES-256 sur votre iPhone avant l'envoi, et la clé ne quitte jamais le trousseau de l'appareil. Les photos et vidéos sont verrouillées derrière Face ID dans le coffre, mais pas encore chiffrées au repos. Nous préférons vous le dire clairement."),
        ("Que se passe-t-il si quelqu'un essaie d'ouvrir mon coffre ?", "Chaque tentative ratée prend discrètement une photo avec la caméra frontale et note l'heure. Avec Safey Pro, vous voyez la photo et tout l'historique."),
        ("Et si je perds mon téléphone ?", "Le coffre est protégé par Face ID, Touch ID ou le code de l'appareil. Vos données se synchronisent en privé : connectez-vous sur un nouvel iPhone pour tout retrouver."),
        ("Safey est-il gratuit ?", "Oui. Safey est gratuit avec 500 Mo. Safey Pro est facultatif, offre 7 jours d'essai gratuit puis se renouvelle au prix affiché dans l'app, sauf résiliation.")],
  guides_eyebrow="Guides", guides_h2="Confidentialité et stockage, expliqués (en anglais).", all_guides="Tous les guides →",
  final_h2="Gardez-le pour vous.", final_p="Téléchargez Safey et protégez vos photos privées, mots de passe et fichiers, gratuitement sur l'App Store.",
  foot_by="un coffre-fort privé par", foot_guides="Guides", foot_privacy="Confidentialité", foot_terms="Conditions",
),
"de": dict(
  title="Safey: Privater Tresor für Fotos & Passwörter (iPhone)",
  desc="Safey ist ein privater Tresor fürs iPhone: Verstecke Fotos und Videos hinter Face ID und speichere Passwörter, Karten und Notizen mit AES-256 verschlüsselt.",
  keywords="fotos verstecken iphone, foto tresor app, app zum fotos verstecken, geheimes album, passwort manager, private app, fotos sperren iphone",
  nav_small="Gratis im", cta_small="Laden im", how_btn="So funktioniert's",
  eyebrow="iOS · Face ID · AES-256", h1=("Der Tresor für alles, was du lieber ", "verborgen hältst", "."),
  lede="Hol private Fotos und Videos aus deiner Mediathek und bewahre Passwörter, Karten, Notizen und Dateien an einem Ort auf, der sich nur mit deinem Gesicht öffnet.",
  chips=["Verschlüsselte Passwörter", "Face-ID-Sperre", "Sperrt sofort"],
  alts=["Startbildschirm des Safey-Tresors", "Passwort-Generator von Safey", "Face-ID-Sperrbildschirm von Safey"],
  caps=["Dein ganzer Tresor, ein Tipp entfernt", "Starke Passwörter mit einem Tipp", "Immer hinter Face ID"],
  how_eyebrow="Das Mediathek-Problem", how_h2="Dein Album „Ausgeblendet“ ist gar nicht versteckt.",
  how_p="Jeder, der dein Handy entsperrt, kann es öffnen. Safey verschiebt private Fotos und Videos in einen Tresor, der sich nur für dich öffnet. So kannst du dein Handy ohne Sorge weitergeben.",
  exposed="Status: <b>offen</b> · jeder kann sie sehen", secured="Status: <b>geschützt</b> · mit Face ID gesperrt",
  lock_btn="Tresor sperren", unlock_btn="Entsperren",
  feat_eyebrow="Ein Tresor statt fünf Apps", feat_h2="Alles Private an einem Ort.",
  feat_p="Die meisten Apps verstecken nur Fotos oder speichern nur Passwörter. Safey hält alles hinter derselben Sperre.",
  feats=[("Versteckte Fotos & Videos", "Raus aus der Mediathek, in ein Face-ID-Album, das niemand sonst öffnet."),
         ("Passwörter & Logins", "Alle Zugänge, mit Generator für starke Passwörter."),
         ("Karten, PINs & CVCs", "Zahlungsdaten verschlüsselt, sichtbar erst nach Gesichtsprüfung."),
         ("Sichere Notizen", "Wiederherstellungscodes, WLAN-Passwörter, Passdaten."),
         ("Einbruchsalarm", "Jeder fehlgeschlagene Versuch fotografiert unbemerkt, wer es probiert."),
         ("Dateien & Dokumente", "Ausweise, Zertifikate und PDFs sicher im Tresor.")],
  sec_eyebrow="So funktioniert die Verschlüsselung", sec_h2="Verschlüsselt, bevor es dein Handy verlässt.",
  sec_p="Passwörter, Karten, CVCs, PINs und Notizen werden auf deinem iPhone mit AES-256 verschlüsselt. Der Schlüssel liegt im Schlüsselbund des Geräts und verlässt ihn nie. Niemand kann sie lesen, kein Angreifer und auch nicht wir.",
  sec_points=["Auf dem Gerät verschlüsselt, vor jeder Synchronisierung", "Der Schlüssel verlässt nie deinen Schlüsselbund", "Fotos und Videos hinter Face ID versteckt"],
  sec_tag="auf dem Gerät verschlüsselt", note_plain="Code für den Wohnungstresor: 4471",
  price_eyebrow="Kostenlos starten", price_h2="Dein ganzer Tresor, kostenlos.",
  price_p="Safey Pro bringt mehr Schutz und Platz, und die ersten 7 Tage sind gratis.",
  tiers=[("GRATIS", "Gratis", "für immer", "Fotos und Videos hinter Face ID, dazu Passwörter, Karten und Notizen mit AES-256 verschlüsselt.", "500 MB inklusive"),
         ("PRO", "50 GB", "ab 2,99 $/Monat", "Sieh, wer einbrechen wollte, nutze einen Täuschungscode und speichere viel mehr.", "7 Tage gratis"),
         ("PRO MAX", "200 GB", "ab 5,99 $/Monat", "Alles aus Pro mit maximalem Platz für deine privaten Dateien.", "7 Tage gratis")],
  faq_eyebrow="Gut zu wissen", faq_h2="Fragen und Antworten.",
  faqs=[("Wie verstecke ich Fotos und Videos auf dem iPhone?", "Öffne den Foto-Tresor in Safey und importiere die Fotos und Videos, die du verstecken willst. Sie landen in einem Face-ID-Album, und du kannst sie aus der Mediathek löschen, damit niemand sie sieht."),
        ("Ist Safey wirklich privat?", "Passwörter, Kartennummern, CVCs, PINs und Notizen werden vor dem Hochladen auf deinem iPhone mit AES-256 verschlüsselt, und der Schlüssel verlässt nie den Schlüsselbund des Geräts. Fotos und Videos sind im Tresor hinter Face ID gesperrt, aber noch nicht im Ruhezustand verschlüsselt. Das sagen wir lieber offen."),
        ("Was passiert, wenn jemand versucht, meinen Tresor zu öffnen?", "Jeder Fehlversuch macht unbemerkt ein Foto mit der Frontkamera und notiert die Uhrzeit. Mit Safey Pro siehst du das Foto und den ganzen Verlauf."),
        ("Was, wenn ich mein Handy verliere?", "Der Tresor ist mit Face ID, Touch ID oder dem Gerätecode geschützt. Deine Daten werden privat synchronisiert, sodass du sie auf einem neuen iPhone per Anmeldung wiederherstellst."),
        ("Ist Safey kostenlos?", "Ja. Safey ist mit 500 MB kostenlos. Safey Pro ist optional, startet mit 7 Tagen gratis und verlängert sich danach zum in der App angezeigten Preis, sofern du nicht kündigst.")],
  guides_eyebrow="Ratgeber", guides_h2="Privatsphäre und Speicher, erklärt (auf Englisch).", all_guides="Alle Ratgeber →",
  final_h2="Bleibt bei dir.", final_p="Lade Safey und schütze private Fotos, Passwörter und Dateien, kostenlos im App Store.",
  foot_by="ein privater Tresor von", foot_guides="Ratgeber", foot_privacy="Datenschutz", foot_terms="Nutzungsbedingungen",
),
"it": dict(
  title="Safey: cassaforte privata per foto e password su iPhone",
  desc="Safey è una cassaforte privata per iPhone: nascondi foto e video dietro Face ID e conserva password, carte e note cifrate sul dispositivo con AES-256.",
  keywords="nascondere foto iphone, cassaforte foto, app per nascondere foto, album segreto, gestore password, app privata, bloccare foto iphone",
  nav_small="Gratis su", cta_small="Scarica su", how_btn="Come funziona",
  eyebrow="iOS · Face ID · AES-256", h1=("La cassaforte per tutto ciò che preferisci ", "tenere nascosto", "."),
  lede="Togli foto e video privati dal rullino e tieni password, carte, note e file in un unico posto che si apre solo con il tuo volto.",
  chips=["Password cifrate", "Blocco con Face ID", "Si blocca all'istante"],
  alts=["Schermata principale della cassaforte Safey", "Generatore di password sicure di Safey", "Schermata di blocco Face ID di Safey"],
  caps=["Tutta la cassaforte, a un tocco", "Password sicure in un tocco", "Sempre dietro Face ID"],
  how_eyebrow="Il problema del rullino", how_h2="Il tuo album \"Nascosti\" non è davvero nascosto.",
  how_p="Chiunque sblocchi il telefono può aprirlo. Safey sposta foto e video privati in una cassaforte che si apre solo per te, così puoi prestare il telefono senza pensieri.",
  exposed="stato: <b>esposto</b> · chiunque può vederle", secured="stato: <b>protetto</b> · bloccato con Face ID",
  lock_btn="Blocca la cassaforte", unlock_btn="Sblocca",
  feat_eyebrow="Una cassaforte, non cinque app", feat_h2="Tutto il privato, in un unico posto.",
  feat_p="Molte app nascondono solo le foto o salvano solo le password. Safey tiene tutto dietro lo stesso blocco.",
  feats=[("Foto e video nascosti", "Fuori dal rullino, in un album con Face ID che nessun altro apre."),
         ("Password e accessi", "Tutti i tuoi accessi, con un generatore di password sicure."),
         ("Carte, PIN e CVC", "Dati di pagamento cifrati, visibili solo dopo il riconoscimento del volto."),
         ("Note sicure", "Codici di recupero, password wifi, dati del passaporto."),
         ("Avvisi di intrusione", "Ogni sblocco fallito scatta di nascosto una foto a chi ci prova."),
         ("File e documenti", "Documenti d'identità, certificati e PDF dentro la cassaforte.")],
  sec_eyebrow="Come funziona la cifratura", sec_h2="Cifrato prima di lasciare il telefono.",
  sec_p="Password, carte, CVC, PIN e note vengono cifrati con AES-256 sul tuo iPhone. La chiave resta nel portachiavi del dispositivo e non lo lascia mai: nessuno può leggerli, né un malintenzionato né noi.",
  sec_points=["Cifrato sul dispositivo, prima di sincronizzare", "La chiave non lascia mai il portachiavi", "Foto e video nascosti dietro Face ID"],
  sec_tag="cifrato sul dispositivo", note_plain="Codice della cassaforte di casa: 4471",
  price_eyebrow="Gratis per iniziare", price_h2="Tutta la cassaforte, gratis.",
  price_p="Safey Pro aggiunge protezione e spazio, e i primi 7 giorni sono gratis.",
  tiers=[("GRATIS", "Gratis", "per sempre", "Foto e video dietro Face ID, più password, carte e note cifrate con AES-256.", "500 MB inclusi"),
         ("PRO", "50 GB", "da 2,99 $/mese", "Guarda il volto di chi ha provato a entrare, usa un codice esca e salva molto di più.", "7 giorni gratis"),
         ("PRO MAX", "200 GB", "da 5,99 $/mese", "Tutto di Pro con il massimo spazio per i tuoi file privati.", "7 giorni gratis")],
  faq_eyebrow="Da sapere", faq_h2="Domande e risposte.",
  faqs=[("Come nascondo foto e video su iPhone?", "Apri la cassaforte foto di Safey e importa le foto e i video da nascondere. Finiscono in un album bloccato con Face ID e puoi eliminarli dal rullino così nessuno li vede."),
        ("Safey è davvero privato?", "Password, numeri di carta, CVC, PIN e note vengono cifrati con AES-256 sul tuo iPhone prima del caricamento, e la chiave non lascia mai il portachiavi del dispositivo. Foto e video sono bloccati dietro Face ID nella cassaforte, ma non sono ancora cifrati a riposo. Preferiamo dirlo chiaramente."),
        ("Cosa succede se qualcuno prova ad aprire la mia cassaforte?", "Ogni tentativo fallito scatta in silenzio una foto con la fotocamera frontale e registra l'ora. Con Safey Pro vedi la foto e la cronologia completa."),
        ("E se perdo il telefono?", "La cassaforte è protetta da Face ID, Touch ID o dal codice del dispositivo. I tuoi dati si sincronizzano in privato e puoi ripristinarli su un nuovo iPhone accedendo."),
        ("Safey è gratis?", "Sì. Safey è gratis con 500 MB. Safey Pro è facoltativo, include 7 giorni di prova gratuita e poi si rinnova al prezzo indicato nell'app, salvo disdetta.")],
  guides_eyebrow="Guide", guides_h2="Privacy e spazio, spiegati (in inglese).", all_guides="Tutte le guide →",
  final_h2="Resta tuo.", final_p="Scarica Safey e proteggi foto private, password e file, gratis sull'App Store.",
  foot_by="una cassaforte privata di", foot_guides="Guide", foot_privacy="Privacy", foot_terms="Termini",
),
"tr": dict(
  title="Safey: iPhone için gizli fotoğraf ve şifre kasası",
  desc="Safey, iPhone için özel bir kasa: fotoğraf ve videoları Face ID arkasına gizle, şifre, kart ve notları cihazda AES-256 ile şifreli sakla.",
  keywords="iphone fotoğraf gizleme, fotoğraf kasası, gizli albüm uygulaması, şifre yöneticisi, gizli kasa, fotoğraf kilitleme",
  nav_small="Ücretsiz", cta_small="İndir", how_btn="Nasıl çalışır",
  eyebrow="iOS · Face ID · AES-256", h1=("", "Gizli kalsın", " istediğin her şeyin kasası."),
  lede="Özel fotoğraf ve videolarını film rulosundan çıkar; şifreleri, kartları, notları ve dosyaları yalnızca yüzünle açılan tek bir yerde sakla.",
  chips=["Şifreli şifreler", "Face ID kilidi", "Anında kilitlenir"],
  alts=["Safey kasa ana ekranı", "Safey güçlü şifre oluşturucu", "Safey Face ID kilit ekranı"],
  caps=["Tüm kasan bir dokunuş uzağında", "Tek dokunuşla güçlü şifreler", "Her zaman Face ID arkasında"],
  how_eyebrow="Film rulosu sorunu", how_h2="\"Gizli\" albümün aslında gizli değil.",
  how_p="Telefonunun kilidini açan herkes onu açabilir. Safey özel fotoğraf ve videolarını yalnızca senin açabildiğin bir kasaya taşır; telefonunu gönül rahatlığıyla verebilirsin.",
  exposed="durum: <b>açıkta</b> · herkes görebilir", secured="durum: <b>korunuyor</b> · Face ID ile kilitli",
  lock_btn="Kasayı kilitle", unlock_btn="Kilidi aç",
  feat_eyebrow="Beş uygulama değil, tek kasa", feat_h2="Tüm özel şeylerin tek yerde.",
  feat_p="Çoğu uygulama ya yalnızca fotoğrafları gizler ya da yalnızca şifreleri saklar. Safey hepsini aynı kilidin arkasında tutar.",
  feats=[("Gizli fotoğraf ve videolar", "Film rulosundan çıkıp başkasının açamayacağı Face ID albümüne."),
         ("Şifreler ve girişler", "Tüm hesapların, güçlü şifre oluşturucuyla."),
         ("Kartlar, PIN ve CVC", "Ödeme bilgileri şifreli, yalnızca yüz doğrulamasından sonra görünür."),
         ("Güvenli notlar", "Kurtarma kodları, Wi-Fi şifreleri, pasaport bilgileri."),
         ("İzinsiz giriş uyarıları", "Her başarısız deneme, deneyen kişinin gizlice fotoğrafını çeker."),
         ("Dosyalar ve belgeler", "Kimlikler, sertifikalar ve PDF'ler kasada güvende.")],
  sec_eyebrow="Şifreleme nasıl çalışır", sec_h2="Telefonundan çıkmadan şifrelenir.",
  sec_p="Şifreler, kartlar, CVC'ler, PIN'ler ve notlar iPhone'unda AES-256 ile şifrelenir. Anahtar cihazının anahtar zincirinde kalır ve oradan hiç çıkmaz; kimse okuyamaz, ne bir saldırgan ne de biz.",
  sec_points=["Senkronizasyondan önce cihazda şifrelenir", "Anahtar anahtar zincirinden hiç çıkmaz", "Fotoğraf ve videolar Face ID arkasında gizli"],
  sec_tag="cihazda şifrelendi", note_plain="Ev kasası kodu: 4471",
  price_eyebrow="Ücretsiz başla", price_h2="Kasanın tamamı ücretsiz.",
  price_p="Safey Pro daha fazla koruma ve alan ekler; ilk 7 gün ücretsizdir.",
  tiers=[("ÜCRETSİZ", "Ücretsiz", "her zaman", "Face ID arkasında fotoğraf ve videolar, ayrıca AES-256 ile şifreli şifre, kart ve notlar.", "500 MB dahil"),
         ("PRO", "50 GB", "aylık 2,99 $'dan", "Girmeye çalışanın yüzünü gör, sahte kod kullan ve çok daha fazlasını sakla.", "7 gün ücretsiz"),
         ("PRO MAX", "200 GB", "aylık 5,99 $'dan", "Pro'nun her şeyi, özel dosyaların için en fazla alanla.", "7 gün ücretsiz")],
  faq_eyebrow="Bilmekte fayda var", faq_h2="Sık sorulan sorular.",
  faqs=[("iPhone'da fotoğraf ve video nasıl gizlenir?", "Safey'in fotoğraf kasasını aç ve gizlemek istediğin fotoğraf ve videoları içe aktar. Face ID ile kilitli bir albüme taşınırlar; film rulosundan silerek kimsenin görmemesini sağlayabilirsin."),
        ("Safey gerçekten gizli mi?", "Şifreler, kart numaraları, CVC'ler, PIN'ler ve notlar yüklenmeden önce iPhone'unda AES-256 ile şifrelenir ve anahtar cihazının anahtar zincirinden hiç çıkmaz. Fotoğraf ve videolar kasada Face ID arkasında kilitlidir ancak henüz bekleme durumunda şifrelenmez. Bunu açıkça söylemeyi tercih ediyoruz."),
        ("Biri kasamı açmaya çalışırsa ne olur?", "Her başarısız deneme ön kamerayla sessizce bir fotoğraf çeker ve saati kaydeder. Safey Pro ile fotoğrafı ve tüm geçmişi görürsün."),
        ("Telefonumu kaybedersem?", "Kasa Face ID, Touch ID veya cihaz koduyla korunur. Verilerin gizli şekilde senkronize olur; yeni bir iPhone'da giriş yaparak her şeyi geri yüklersin."),
        ("Safey ücretsiz mi?", "Evet. Safey 500 MB ile ücretsizdir. Safey Pro isteğe bağlıdır, 7 günlük ücretsiz denemeyle başlar ve iptal etmezsen uygulamada gösterilen fiyattan yenilenir.")],
  guides_eyebrow="Rehberler", guides_h2="Gizlilik ve depolama rehberleri (İngilizce).", all_guides="Tüm rehberler →",
  final_h2="Senin kalsın.", final_p="Safey'i indir; özel fotoğraflarını, şifrelerini ve dosyalarını koru. App Store'da ücretsiz.",
  foot_by="özel bir kasa:", foot_guides="Rehberler", foot_privacy="Gizlilik", foot_terms="Koşullar",
),
"id": dict(
  title="Safey: Brankas privat untuk foto dan kata sandi di iPhone",
  desc="Safey adalah brankas privat untuk iPhone: sembunyikan foto dan video di balik Face ID, simpan kata sandi, kartu, dan catatan terenkripsi AES-256 di perangkat.",
  keywords="sembunyikan foto iphone, brankas foto, aplikasi penyembunyi foto, album rahasia, pengelola kata sandi, aplikasi privat, kunci foto iphone",
  nav_small="Gratis di", cta_small="Unduh di", how_btn="Cara kerjanya",
  eyebrow="iOS · Face ID · AES-256", h1=("Brankas untuk semua yang ingin ", "tetap tersembunyi", "."),
  lede="Pindahkan foto dan video pribadi dari rol kamera, lalu simpan kata sandi, kartu, catatan, dan file di satu tempat yang hanya terbuka dengan wajahmu.",
  chips=["Kata sandi terenkripsi", "Kunci Face ID", "Terkunci seketika"],
  alts=["Layar utama brankas Safey", "Pembuat kata sandi kuat Safey", "Layar kunci Face ID Safey"],
  caps=["Seluruh brankasmu, sekali ketuk", "Kata sandi kuat sekali ketuk", "Selalu di balik Face ID"],
  how_eyebrow="Masalah rol kamera", how_h2="Album \"Tersembunyi\" sebenarnya tidak tersembunyi.",
  how_p="Siapa pun yang membuka kunci ponselmu bisa membukanya. Safey memindahkan foto dan video pribadimu ke brankas yang hanya terbuka untukmu, jadi kamu bisa meminjamkan ponsel tanpa khawatir.",
  exposed="status: <b>terbuka</b> · siapa pun bisa melihat", secured="status: <b>aman</b> · terkunci Face ID",
  lock_btn="Kunci brankas", unlock_btn="Buka kunci",
  feat_eyebrow="Satu brankas, bukan lima aplikasi", feat_h2="Semua yang pribadi, di satu tempat.",
  feat_p="Kebanyakan aplikasi hanya menyembunyikan foto atau hanya menyimpan kata sandi. Safey menyimpan semuanya di balik kunci yang sama.",
  feats=[("Foto dan video tersembunyi", "Keluar dari rol kamera, masuk ke album Face ID yang tak bisa dibuka orang lain."),
         ("Kata sandi dan login", "Semua akunmu, dengan pembuat kata sandi kuat."),
         ("Kartu, PIN, dan CVC", "Data pembayaran terenkripsi, hanya terlihat setelah verifikasi wajah."),
         ("Catatan aman", "Kode pemulihan, kata sandi wifi, data paspor."),
         ("Peringatan penyusup", "Setiap gagal membuka kunci diam-diam memotret orang yang mencoba."),
         ("File dan dokumen", "KTP, sertifikat, dan PDF aman di dalam brankas.")],
  sec_eyebrow="Cara kerja enkripsi", sec_h2="Terenkripsi sebelum meninggalkan ponselmu.",
  sec_p="Kata sandi, kartu, CVC, PIN, dan catatan dienkripsi dengan AES-256 di iPhone kamu. Kuncinya tetap di Keychain perangkat dan tidak pernah keluar, jadi tak ada yang bisa membacanya, baik peretas maupun kami.",
  sec_points=["Dienkripsi di perangkat sebelum sinkronisasi", "Kunci tidak pernah keluar dari Keychain", "Foto dan video tersembunyi di balik Face ID"],
  sec_tag="terenkripsi di perangkat", note_plain="Kode brankas rumah: 4471",
  price_eyebrow="Gratis untuk mulai", price_h2="Seluruh brankasmu, gratis.",
  price_p="Safey Pro menambah perlindungan dan ruang, dan 7 hari pertama gratis.",
  tiers=[("GRATIS", "Gratis", "selamanya", "Foto dan video di balik Face ID, plus kata sandi, kartu, dan catatan terenkripsi AES-256.", "Termasuk 500 MB"),
         ("PRO", "50 GB", "mulai $2,99/bulan", "Lihat wajah orang yang mencoba masuk, pakai kode umpan, dan simpan jauh lebih banyak.", "7 hari gratis"),
         ("PRO MAX", "200 GB", "mulai $5,99/bulan", "Semua fitur Pro dengan ruang maksimal untuk file pribadimu.", "7 hari gratis")],
  faq_eyebrow="Perlu diketahui", faq_h2="Pertanyaan umum.",
  faqs=[("Bagaimana cara menyembunyikan foto dan video di iPhone?", "Buka brankas foto Safey dan impor foto serta video yang ingin disembunyikan. Semuanya masuk ke album yang terkunci Face ID, dan kamu bisa menghapusnya dari rol kamera agar tak terlihat orang lain."),
        ("Apakah Safey benar-benar privat?", "Kata sandi, nomor kartu, CVC, PIN, dan catatan dienkripsi dengan AES-256 di iPhone sebelum diunggah, dan kuncinya tidak pernah keluar dari Keychain perangkat. Foto dan video terkunci di balik Face ID di dalam brankas, tetapi belum dienkripsi saat tersimpan. Kami lebih suka mengatakannya dengan jujur."),
        ("Apa yang terjadi jika seseorang mencoba membuka brankasku?", "Setiap percobaan gagal diam-diam memotret dengan kamera depan dan mencatat waktunya. Dengan Safey Pro kamu bisa melihat fotonya dan riwayat lengkap."),
        ("Bagaimana jika ponselku hilang?", "Brankas dilindungi Face ID, Touch ID, atau kode perangkat. Datamu tersinkron secara privat sehingga bisa dipulihkan di iPhone baru dengan masuk ke akun."),
        ("Apakah Safey gratis?", "Ya. Safey gratis dengan 500 MB. Safey Pro bersifat opsional, diawali uji coba gratis 7 hari, lalu diperpanjang sesuai harga di aplikasi kecuali dibatalkan.")],
  guides_eyebrow="Panduan", guides_h2="Privasi dan penyimpanan, dijelaskan (dalam bahasa Inggris).", all_guides="Semua panduan →",
  final_h2="Tetap milikmu.", final_p="Unduh Safey dan lindungi foto pribadi, kata sandi, dan filemu, gratis di App Store.",
  foot_by="brankas privat dari", foot_guides="Panduan", foot_privacy="Privasi", foot_terms="Ketentuan",
),
}

GUIDES = [  # English guides — linked from every locale as crawl paths
    ("/blog/hide-photos-iphone/", "How to Hide Photos on iPhone"),
    ("/blog/best-photo-vault-apps-iphone/", "The Best Photo Vault Apps for iPhone"),
    ("/blog/break-in-alerts-photo-vault/", "How to Know If Someone Tried to Open Your Phone"),
    ("/blog/decoy-passcode-iphone/", "Decoy Passcode: Open an Empty Vault Under Pressure"),
    ("/blog/free-up-storage-iphone/", "How to Free Up Storage on iPhone Without Deleting Photos"),
    ("/blog/safey-vs-keepsafe/", "Safey vs KeepSafe: The Best Free Photo Vault Alternative"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def hreflang_block():
    lines = [f'<link rel="alternate" hreflang="{l}" href="https://safey.app{p}">' for l, (p, _) in ALL.items()]
    lines.append('<link rel="alternate" hreflang="x-default" href="https://safey.app/">')
    return "\n".join(lines)


def store_btn(small):
    return f'<a class="btn btn-primary" href="{STORE}" rel="noopener"><span><small>{small}</small><span class="big">App&nbsp;Store</span></span></a>'


def main_html(t):
    chips = "\n          ".join(f'<span class="chip">{i} {esc(c)}</span>' for i, c in zip(CHIP_ICONS, t["chips"]))
    imgs = "\n              ".join(f'<img src="/assets/{f}" alt="{esc(a)}" width="292" height="610">'
                                   for f, a in zip(["02_dashboard.png", "03_generator.png", "06_lock.png"], t["alts"]))
    shots = "\n          ".join(f'<div class="shot"><img src="https://images.unsplash.com/{s}?auto=format&fit=crop&w=400&q=70" alt="" loading="lazy"><div class="veil">{LOCK}</div></div>' for s in SHOTS)
    feats = "\n        ".join(f'<div class="frow"><span class="fi">{i}</span><div><h3>{esc(h)}</h3><p>{esc(p)}</p></div></div>'
                               for i, (h, p) in zip(FEAT_ICONS, t["feats"]))
    points = "\n          ".join(f"<li>{CHECK} {esc(p)}</li>" for p in t["sec_points"])
    tiers = "\n      ".join(
        f'<div class="tier{" pop" if n == 1 else ""}"><span class="tag">{esc(tag)}</span><div class="amt">{esc(amt)}</div><div class="per">{esc(per)}</div><p class="cap">{esc(cap)}</p><span class="pill">{esc(pill)}</span></div>'
        for n, (tag, amt, per, cap, pill) in enumerate(t["tiers"]))
    faqs = "\n      ".join(f'<details{" open" if n == 0 else ""}><summary>{esc(q)} <span class="plus"></span></summary><div class="body">{esc(a)}</div></details>'
                           for n, (q, a) in enumerate(t["faqs"]))
    guides = "\n        ".join(f'<a href="{u}" lang="en" style="display:block;padding:16px 18px;border:1px solid var(--line,#1f3d40);border-radius:12px;color:inherit;text-decoration:none">{esc(x)}</a>' for u, x in GUIDES)
    h1a, h1b, h1c = t["h1"]
    return f"""<main>
  <!-- HERO -->
  <header class="hero">
    <div class="wrap hero-grid">
      <div>
        <span class="eyebrow load d1">{esc(t["eyebrow"])}</span>
        <h1 class="load d2">{esc(h1a)}<span class="accent">{esc(h1b)}</span>{esc(h1c)}</h1>
        <p class="lede load d3">{esc(t["lede"])}</p>
        <div class="cta-row load d4">
          {store_btn(esc(t["cta_small"]))}
          <a class="btn btn-ghost" href="#how">{esc(t["how_btn"])}</a>
        </div>
        <div class="badges load d4">
          {chips}
        </div>
      </div>
      <div class="stage" id="carousel">
        <div class="stage-glow"></div>
        <div class="phone">
          <div class="notch"></div>
          <div class="screen">
            <div class="track" id="track">
              {imgs}
            </div>
          </div>
        </div>
        <div class="dots" id="dots"></div>
        <p class="caption" id="caption">{esc(t["caps"][0])}</p>
      </div>
    </div>
  </header>

  <!-- LOCK DEMO -->
  <section id="how">
    <div class="wrap lock-demo">
      <div class="lock-copy reveal">
        <span class="eyebrow">{esc(t["how_eyebrow"])}</span>
        <h2>{esc(t["how_h2"])}</h2>
        <p>{esc(t["how_p"])}</p>
        <div class="lock-bar">
          <span class="lock-state" id="lockState">{t["exposed"]}</span>
          <button class="btn btn-primary lock-toggle" id="lockBtn" aria-pressed="false">{esc(t["lock_btn"])}</button>
        </div>
      </div>
      <div class="gallery" id="gallery" aria-live="polite">
        <div class="gallery-grid">
          {shots}
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURES -->
  <section>
    <div class="wrap features">
      <div class="features-intro reveal">
        <span class="eyebrow">{esc(t["feat_eyebrow"])}</span>
        <h2>{esc(t["feat_h2"])}</h2>
        <p>{esc(t["feat_p"])}</p>
      </div>
      <div class="flist stagger">
        {feats}
      </div>
    </div>
  </section>

  <!-- SECURITY -->
  <section class="security">
    <div class="wrap sec-grid">
      <div class="sec-copy reveal">
        <span class="eyebrow">{esc(t["sec_eyebrow"])}</span>
        <h2>{esc(t["sec_h2"])}</h2>
        <p>{esc(t["sec_p"])}</p>
        <ul class="sec-points">
          {points}
        </ul>
      </div>
      <div class="crypt reveal" id="crypt">
        <div class="crypt-top"><i></i><i></i><i></i><span>secure enclave</span></div>
        <div class="crypt-line"><span class="k">note</span>  → <span class="plain" id="cText">{esc(t["note_plain"])}</span></div>
        <div class="crypt-line"><span class="k">aes-256</span> → <span class="cipher" id="cCipher">sfy1:••••••••••••••••••••</span></div>
        <span class="crypt-tag"><svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" stroke="currentColor" stroke-width="1.8"/></svg> {esc(t["sec_tag"])}</span>
      </div>
    </div>
  </section>

  <!-- PRICING -->
  <section>
    <div class="sec-head reveal">
      <span class="eyebrow">{esc(t["price_eyebrow"])}</span>
      <h2>{esc(t["price_h2"])}</h2>
      <p>{esc(t["price_p"])}</p>
    </div>
    <div class="wrap"><div class="tiers stagger">
      {tiers}
    </div></div>
  </section>

  <!-- FAQ -->
  <section>
    <div class="sec-head reveal"><span class="eyebrow">{esc(t["faq_eyebrow"])}</span><h2>{esc(t["faq_h2"])}</h2></div>
    <div class="wrap"><div class="faq stagger">
      {faqs}
    </div></div>
  </section>

  <!-- GUIDES (English, as crawl paths) -->
  <section class="guides">
    <div class="wrap">
      <div class="sec-head reveal"><span class="eyebrow">{esc(t["guides_eyebrow"])}</span><h2>{esc(t["guides_h2"])}</h2></div>
      <div class="guide-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-top:8px">
        {guides}
      </div>
      <p style="margin-top:16px"><a href="/blog/" style="color:var(--brand,#07BEB8)">{esc(t["all_guides"])}</a></p>
    </div>
  </section>

  <!-- FINAL CTA -->
  <section class="final">
    <div class="wrap"><div class="final-card reveal">
      <h2>{esc(t["final_h2"])}</h2>
      <p>{esc(t["final_p"])}</p>
      <div class="cta-row">{store_btn(esc(t["cta_small"]))}</div>
    </div></div>
  </section>
</main>"""


def lang_links(current):
    return "\n      ".join(f'<a href="{p}" hreflang="{l}" lang="{l}">{n}</a>' for l, (p, n) in ALL.items() if l != current)


def footer(t, lang):
    return f"""<footer>
  <div class="wrap foot-row">
    <div>© 2026 Safey — {esc(t["foot_by"])} <a href="https://khatibdesigns.com" style="color:var(--ink-2)">Khatib Designs</a>.</div>
    <div class="foot-links">
      <a href="{STORE}">App Store</a>
      <a href="/blog/">{esc(t["foot_guides"])}</a>
      <a href="/privacy/">{esc(t["foot_privacy"])}</a>
      <a href="/terms/">{esc(t["foot_terms"])}</a>
    </div>
    <div class="foot-links" style="margin-top:10px">
      {lang_links(lang)}
    </div>
  </div>
</footer>"""


def schema(t, lang):
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Safey",
           "operatingSystem": "iOS", "applicationCategory": "UtilitiesApplication", "inLanguage": lang,
           "description": t["desc"], "url": f"https://safey.app/{lang}/", "downloadUrl": STORE,
           "publisher": {"@type": "Organization", "name": "Khatib Designs", "url": "https://khatibdesigns.com"},
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang,
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faqs"]]}
    return (f'<script type="application/ld+json">\n{json.dumps(app, ensure_ascii=False)}\n</script>\n'
            f'<script type="application/ld+json">\n{json.dumps(faq, ensure_ascii=False)}\n</script>')


def sub(pattern, repl, s, flags=re.S):
    out, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    assert n == 1, f"pattern not found: {pattern[:60]}"
    return out


def build(lang, t):
    s = BASE
    url = f"https://safey.app/{lang}/"
    s = sub(r'<html lang="en">', f'<html lang="{lang}">', s)
    s = sub(r"<title>.*?</title>", f"<title>{esc(t['title'])}</title>", s)
    s = sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(t["desc"])}">', s)
    s = sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">', s)
    s = sub(r'(<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n?)+', hreflang_block() + "\n", s)
    s = sub(r'<meta name="keywords" content=".*?">', f'<meta name="keywords" content="{esc(t["keywords"])}">', s)
    s = sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{esc(t["title"])}">', s)
    s = sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{esc(t["desc"])}">', s)
    s = sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{url}">', s)
    s = sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{esc(t["title"])}">', s)
    s = sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{esc(t["desc"])}">', s)
    s = sub(r'<a class="lang" href="/ar/">العربية</a>', '<a class="lang" href="/">English</a>', s)
    s = sub(r"<small>Free on the</small>", f"<small>{esc(t['nav_small'])}</small>", s)
    s = sub(r'<a class="brand" href="/">', f'<a class="brand" href="/{lang}/">', s)
    s = sub(r"<main>.*?</main>", main_html(t), s)
    s = sub(r"<footer>.*?</footer>", footer(t, lang), s)
    s = sub(r'(<script type="application/ld\+json">.*?</script>\s*){2}', schema(t, lang) + "\n\n", s)
    s = sub(r"var caps = \[.*?\];", "var caps = " + json.dumps(t["caps"], ensure_ascii=False) + ";", s)
    s = sub(r"lockBtn\.textContent = locked \? 'Unlock' : 'Lock the vault';",
            f"lockBtn.textContent = locked ? {json.dumps(t['unlock_btn'], ensure_ascii=False)} : {json.dumps(t['lock_btn'], ensure_ascii=False)};", s)
    s = sub(r"lockState\.innerHTML = locked \? '.*?' : '.*?';",
            f"lockState.innerHTML = locked ? {json.dumps(t['secured'], ensure_ascii=False)} : {json.dumps(t['exposed'], ensure_ascii=False)};", s)
    s = sub(r"b\.setAttribute\('aria-label','Screen '\+\(i\+1\)\);", "b.setAttribute('aria-label', String(i+1));", s)
    # assets are referenced relatively on the root page; make them absolute
    s = s.replace('src="assets/', 'src="/assets/').replace('href="assets/', 'href="/assets/')
    out = ROOT / lang / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s)
    return out


def sync_hreflang(path):
    """Write the full hreflang set (and footer language links) into an existing page."""
    p = ROOT / path
    s = p.read_text()
    s = sub(r'(<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n?)+', hreflang_block() + "\n", s)
    p.write_text(s)


if __name__ == "__main__":
    for lang, t in T.items():
        print("wrote", build(lang, t))
    for p in ["index.html", "ar/index.html"]:
        sync_hreflang(p); print("hreflang synced", p)
