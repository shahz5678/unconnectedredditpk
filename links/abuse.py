# coding=utf-8
CORE_ENGLISH_ABUSE_WORDS = ['fuck','fck','fvck','fuk','fuq','phuck','phuk','phuc','phvk','sex','seks','s-e-x','s_e_x','s.e.x','s.e_x','s.e-x','s-e.x',\
's_e.x','s-e_x','s_e-x','pusy','pussy','pssy','dick','penis','cock','vagina','vulva','boob','breast','pimp','whore','asshole','bastard','pubic','piss',\
'shit','idiot','bitch','jackass','balls','testicle','sekks','cunt','fart','clit','asswhole','a_s_s','a-s-s','b00b','blowjob','blojob','booob','3some',\
'boooob','booooob','booooooob','c0ck','cumshot','cumsh0t','d1ck','dildo','dlck','f4nny','faggot','fcuk','f_u_c_k','gangbang','nigga','s_3-x',\
'n1gga','n1gger','nigger','poop','p00p','p0op','po0p','rectum','sh1t','shemale','titties','viagra','turd','wanker','erotic','hooker','incest',\
'intercourse','milf','m1lf','nipple','pig','rape','rapist','rap1st','rap!st','raping','rap1ng','sodom','threesome','topless','upskirt','vibrator',\
'vibrater','vibratur','vibrat0r','douche','doosh','d00sh','se-x','s-ex','se.x','se.x','h0m0','shema1e','c1it','b1owjob','b000b','xx','x-x','tits',\
'x_x','x.x','nude','naked','n!gger','b!tch','pen!s','d!ck','b0ob','bo0b','buub','h00ker','h0mo','hom0','cl!t','rektum','v!agra','assho1e','assh0le',\
'assh01e','n!gga','ballz','bawls','bawlz','vag1na','vag!na','pen1s','pinis','peenus','p1g','p!g','shema!e','shimale','shima1e','top1ess','top!ess',\
'b1tch','brest','vu1va','p1mp','sh!t','p!mp','wh0re','porkistan','p0rkistan','pork!stan','p0rk!stan','porkistaan','p0rkistaan','pork!staan','p0rk!staan'\
'porkystan','p0rkystan','porkystaan','p0rkystaan','puup','kock','licker','1icker','l!cker','1!cker','n1pple','nipp1e','n1pp1e','n!pp1e','n!pp!e','f-ck',\
'f_ck','f.ck','porki-stan','porki.stan','porki_stan','fack','feck','porkies','p0rkies','pork!es','p0rk!es','s3x','s3ks','s-3-x','s_3_x','s.3.x','s.3_x',\
's.3-x','s-3.x','s_3.x','s-3_x','sxsy','pron','romantic','rommantic','naughty','bobs','sixy','sx','x.xx','leon','romentic','lesb','sax','s@x','f.u.k',\
'vegina','se_x','leso','vigina','pen@is','ediut','kiss','b0o0b','b.o.o.b','sixe','shemaale','cex','iesbo','fu-ck','sperm','xnx','penes','s+e+x+y','sucker',\
'girlfriend','boyfriend','couple','romance','klss','_hot_','-hot-','_hot-','-hot_','.hot.','_hot.','-hot.','.hot-','.hot_','_h0t_','-h0t-','_h0t-','-h0t_',\
'.h0t.','_h0t.','-h0t.','.h0t-','.h0t_','sekxy','l_e_s_b','l-e-s-b','l.e.s.b','lezb','horny','h0rny','7inch','8inch','9inch','10inch','11inch','12inch',\
'seexy','1.on.1','hsband','lesvian','saaxy','nepples','f-u-c-k','lsbian','buoob','bu00b','biitCh','nipals','hotchat','pussi','sixie']#'semen','anus',butt','kok','anal','ana1','hot','fanny','qhus'


CORE_URDU_ABUSE_WORDS = ['aunty','besharm','baysharm','phudd','phudi','phodi','lun','choot','gashti','gandu','luun','gshti','randi','rndi','hijra','phatti','nanga',\
'nangi','phddi','phdi','lanat','taxi','taksi','kutta','kutti','kutty','gaand','gaaand','chut','lul','harami','bharw','bhrrw','bharv','bhrrv','bharw','phutti','chod',\
'kuss','mujra','mjra','mojra','bund','tawaif','twaif',' dalla ','dlla','chdai','chudai','bhosra','bhosri','bhosre','mammay','mammey','lora','lowra','khuss','qus',\
'bhosri','bhosry','bosri','bosry','phati','phtti','phti','phoodi','pyasi','pyasa','piyasa','piyasi','payasi','payasa','bh0sre','bh0sri','bh0sry','b0sry','b0sre','b0sri',\
'ch0d','ch00d','chood','l0ra','lorra','l0wra','1un','phud!','phu.di','gasht!','1anat','da11a','d11a','h!jra','hijjra','hjra','khassi','qhassi','khasi','qhasi','kutte','luuun',\
'rundi','rund!','sooar','suar','suer','sooer','soowar','soower','suuer','suuar','mamey','bhosad','bhosd','ch00t',' muth ','bhosda','choos','chodun','chodho','chuda!',\
'lorray',' gand ','phdy','1orra','1ora','ghasti','gasti','gast!','chuse','charh','randee','randy','rande','rand!','tatta','tatay','tutta','tutty','tutti','tatti',\
'tatey','tetti',' tati ','gasht1','gast1','gand','rand1','tutt1','tatt1','tatte','tutte','tutta','mumma','kanjar','kunjur','kunjer','kanjer','kanjr','kenjr','kanjjar'\
,'kannjar','canjar','canjer','kenjer','kuta','kutey','kutay','k@njr','qutay','fuddi','fudi','fudddi','phdddi','chaval','podi','p0di','p0d!','pudd!','pudi','pudy','pudda',\
'puddda','pdda','yawan','yaawan','khusra','kusra','qhusra','qusra','yawaan','yavan','yaavan','yavaan','yuvai','yuwai','yuvay','yvai','ywai','yave','ph-ddi','ph_ddi',\
'ph.ddi','hij-ra','h1jra','h!jra','ran-di','ran_di','ran.di','hij.ra','h1j.ra','qhussra','khussra','kuty','p.h.u.d.i','p.h.u.d.d.i','l.u.n','g.a.n.d','r.a.n.d.i',\
'g.a.s.h.t.i','h.i.j.r.a','c.h.o.o.t','p.h.o.d.i','l.u.u.n','g.s.h.t.i','r.n.d.i','k.u.s.s','k.h.u.s.s','1.u.n','h.1.j.r.a','k.a.n.j.a.r','f.u.d.d.i','f.u.d.i',\
'p.o.d.i','p.u.d.d.a','p.u.d.d.d.a','k.h.u.s.r.a','yavai','y.a.v.a.i','y.u.v.a.i','l.u.l','c.h.o.d','s.u.a.r','p.d.d.a','k.h.a.s.s.i','k.h.a.s.i','hijry','hijre',\
'h!jry','h!jre','phudy','phody','khassy','yavay','r@ndi','naangi','behn','bahn','bhen','-ki-','.ki.','_ki_','-ki_','_ki-','.ki_','_ki.','.ki-','-ki.','-ke-','.ke.',\
'_ke_','-ke_','_ke-','.ke_','_ke.','.ke-','-ke.','gasshti','chuut','kanjjri','ghashti','ranndy','behen','behan','bahan','phuda','ph0d','hawas','havas','bgarat','lorro'\
,'bhan','bhund','g@ndo','phoudi','puddi','puudi','chout','ganndi','ch0ut','hrami','kuuttii','l00ra','gaaaando','marwani','tharki','th@rki','th4rki','bgairat','raandi',\
'gannd','knjr','rnnd','gndo','bhn','gnd','pyar','garum','chudakar','thko','phude','fhudiyo','chudwa','phudda','ghushti','jismani','chot','xhodo','thoko','ch0t','lu.n',\
'hiijra','chadwa','pyase','l0n','ghand','gndo','dewani','dewana','uff','uuf','phuud','chdwa','ghsti','iun','knnjr','gnnd','gasht','gsht','barwy','l_u_n','ch0s','-l-','.l.',\
'_l_','@l@','-l_','_l-','.l_','_l.','.l-','-l.','@l.','@l_','@l-','.l@','_l@','-l@','lool','looora','lauda','gaaram','chosn','gaasht','chudo','puda','bhond','b-0-0-b',\
'r-a-n-d-i','lolla','raaaand','phouuuudi','phar','c.h.u.d.a.i','p0ddi','c.u.d.a.i','gaaaand','ghhashti','c.h.u.t','phuti','ch_ut','ga-nddo','l-esbo','bnd','chdi','gannnd',\
'choso','leooon','chooopa','chuddakr','gondo','chuuut','peenis','chudaye','ph.udi','thrki','kmeni','chusti','codu','gan.do','cho0t','thuko','tharak','aunti','poddi',\
'mammy','hotlark','hotbachi','bh3n','phidi','ph0ud','chuudai','s3cs','phudh','thark1','g@@nd','g@nd','ch@@t','phrne','randhi','thaarki','mamy']#salle,lanti,lant,soor,ph0di,ph0de


CORE_POLITICALLY_SENSITIVE_WORDS = ['isis','hitler','hit1er','h!tler','h!t1er','h1t!er','hytler','hyt1er','hitla','hit1a','h!t1a','h!t!er','1s1s',\
'!s!s','is-is','is_is','is.is','terrorist','terr0rist','terror!st','terr0r!st','terorist','ter0rist','teror!st','ter0r!st','hindutva','hindutwa',\
'i.s.i.s','h.i.t.l.e.r','iluminati','illuminati']


MISC_POLITICALLY_SENSITIVE_WORDS = ['india','america','amreeka','amrika','bharat','bharti','bharty','bhartee','umreeka','umrika',\
'hindustan','israel','indya','inddia','amrica','izrael','yahoodi','yah00di','yh00di','yhoodi','yahood!','hindu','h!ndu','hindoo',\
'moslem','muzlim','mus1im','musl!m','mus1!m','yahudi','yahud!']


CORE_RELIGIOUSLY_SENSITIVE_WORDS = ['bhagwan','kafir','qafir','kafr','qafr','kfir','qfir','kaphir','qaphir','kaf1r','kaf!r','a11ah','bhagvan',\
'kafur','bhagwaan','bagwan','bagwaan','bagvaan','jesus','ahmedi','haraam','haaraam','haraaam','ka-fir','ka-f!r','ka_f!r','ka-ph!r','ka-ph1r','yazeed',\
'qa-fir','qa-f!r','qa-f1r','athiest','atheist','atheism','athiesm','sipah','taliban','ta1iban','talibaan','tal!baan','tal!ban','talyban','talybaan','god',\
'taaliban','taa1iban','allaah','blasphemy','kufr','qufr','sippa','s!ppa','s!pah','fatwa','fatva','ftva','bhagvaan','k.a.f.i.r','q.a.f.i.r','k.a.f.r',\
'k.f.i.r','q.a.f.r','q.f.i.r','k.a.p.h.i.r','q.a.p.h.i.r','k.a.f.!.r','q.a.f.!.r','k.a.f.u.r','kafer','qafer','kaffer','qaffer','kaffur','qaffur',\
'h.a.r.a.m','h.a.r.a.a.m']#haram, ahmadi, ftwa


MISC_SENSITIVE_WORDS = ['fahashi','jinsi','garam','kartoot','qartoot','kart00t','qart00t','kartut','qartut','karto0t','kart0ot','qart0ot','qarto0t',\
'krtut','qrtut','kertut','kert00t','kertoot','qertoot','qert00t','idiot','idi0t','id!ot','id!0t','1diot','damn','kat!l','scandal','scandle','scendel',\
'skendel','skendl','scandl','scendl','sharmnaak','sharamnaak','sharamnaaq','sharmnaaq','shrmnaak','shrmnaaq','jinsy','j!nsy','j!nsi','porn','p0rn',\
'sharamnak','p-o-r-n','p_o_r_n','p.o.r.n','p-o_r-n','p_o-r_n','p-o_r_n','p_o_r-n','mhb','m_h_b','m-h-b','m.h.b','m-h_b','m_h-b','m.h_b','m_h.b','m-h.b',\
'm.h-b','mh.b','m.h@b','murdabad','mrdabad','kharish','doodh','1on1','ejacu']

SOLICITATION_WORDS = ['whatapp','whatsap','watsap','whtsap','whtapp','facebook','facebuk','facebok','telenor','mobilink','zong','ufone','warid',\
'telen0r','m0bilink','z0ng','facbook']

BANNED_FORGOTTEN_NICKS = ['fuck','sex','phudd','phudi','phodi','lun','choot','pussy','boob','xx','breast','penis','hitler','gasht','gandu','luun',\
'mhb','allah','bhagwan','allaah','quran','jesus','Damadam-Feedback','Damadam-Admin']

CONTEXTUALLY_SENSITIVE_WORDS = ['allah','pakistan','muslim','admin','pakistn','pakistaan','pkistan']

FLAGGED_PUBLIC_TEXT_POSTING_WORDS = ['1 on 1', 'invite', ' hot ', 'lun', 'girl', 'bye', 'new', 'sex', ' fan ', 'sis', 'join', 'boring', 'private',\
'married', 'prvt', 'bored', 'fake', 'invt', 'pvt', 'copy', 'ldki', 'grl', 'noon', 'allah', 'طلاق'.decode('utf-8'), 'یافتہ'.decode('utf-8')]

BANNED_NICKS = CORE_ENGLISH_ABUSE_WORDS+CORE_URDU_ABUSE_WORDS+CORE_POLITICALLY_SENSITIVE_WORDS+MISC_POLITICALLY_SENSITIVE_WORDS+\
CORE_RELIGIOUSLY_SENSITIVE_WORDS+MISC_SENSITIVE_WORDS+SOLICITATION_WORDS+CONTEXTUALLY_SENSITIVE_WORDS


BANNED_MEHFIL_TOPIC_WORDS = CORE_ENGLISH_ABUSE_WORDS+CORE_URDU_ABUSE_WORDS+CORE_POLITICALLY_SENSITIVE_WORDS+CORE_RELIGIOUSLY_SENSITIVE_WORDS+\
MISC_SENSITIVE_WORDS+SOLICITATION_WORDS


BANNED_MEHFIL_RULES_WORDS = CORE_ENGLISH_ABUSE_WORDS+CORE_URDU_ABUSE_WORDS+CORE_POLITICALLY_SENSITIVE_WORDS+CORE_RELIGIOUSLY_SENSITIVE_WORDS