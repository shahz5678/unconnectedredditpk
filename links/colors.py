#HOW TO ADD A PRIMARY COLOR
#HOW TO REMOVE A PRIMARY COLOR
#HOW TO ADD A SECONDARY COLOR
#HOW TO REMOVE A SECONDARY COLOR

# num(PRIMARY_COLORS) = 15
PRIMARY_COLORS = [\
#turquoise
"#01edd2",\
#pink (v1)
"#fa88a3",\
#dull pink
"#e378ba",\
#electric pink
"#f574ff",\
#blue
"#6292ff",\
#green (v1)
"#5cf48c",\
#firozi (v1)
"#2ed7e1",\
#purple (v1)
"#977aff",\
#sky-teal-blue
"#28d7ff",\
#gold (v1)
"#f4d140",\
#coral
"#f88379",\
#medium purple
"#c66aff",\
#greenish yellow
"#d4d900",\
#orange (v1)
"#ffbe69",\
#light mint green
"#00f0a9"
]

# num(SECONDARY_COLORS) = 62
SECONDARY_COLORS = [\
#turquoise
"#01edd2",\
#medium purple
"#c66aff",\
#light electric pink (v1)
"#eb61ff",\
#light electric pink (v2)
"#fc90ff",\
#electric pink
"#f574ff",\
#dark electric pink
"#ff60e1",\
#coral
"#f88379",\
#purple (v1)
"#977aff",\
#purple (v2)
"#a971fc",\
#purple (v3)
"#b76eff",\
#purple (v4)
"#d985f7",\
#purple (v5)
"#7f5fff",\
#purple (v6)
"#a991ff",\
#purple (v7)
"#a293ff",\
#pink (v2)
"#ff7d9c",\
#pink (v3)
"#fc98bc",\
#reddish (v1)
"#ff5f5f",\
#reddish (v2)
"#ff5a5a",\
#tomato
"#ff8282",\
#greenish yellow
"#d4d900",\
#greenish
"#c8ff28",\
#aquamarine (v1)
"#28ffaa",\
#aquamarine (v2)
"#00eccb",\
#firozi (v2)
"#2ff6ea",\
#firozi (v3)
"#49d9ff",\
#firozi (v4)
"#31e6ed",\
#dull green
"#89e46c",\
#mint greenish
"#9de245",\
#mint green
"#66ff3a",\
#light mint green
"#00f0a9"
#light green
"#a5ed31",\
#green (v2)
"#2ff06f",\
#green (v3)
"#26e99c",\
#green (v4)
"#42ec72",\
#green (v5)
"#46ec5c",\
#green (v6)
"#50f777",\
#green (v7)
"#01f5a1",\
#green (v8)
"#42e966",\
#green (v9)
"#52f578",\
#sky blue (v1)
"#69baf5",\
#sky blue (v2)
"#6d9eff",\
#sky blue (v3)
"#32a8f8",\
#sky blue (v4)
"#5caeff",\
#sky blue (v5)
"#7ba6fc",\
#blue
"#6292ff",\
#sky-teal-blue
"#28d7ff",\
#purple blue
"#9380ff",\
#teal-blue (v1)
"#3bc1f0",\
#teal-blue (v2)
"#34caf0",\
#teal-blue (v3)
"#01b0ed",\
#gold (v2)
"#f9cd48",\
#gold (v3)
"#fed940",\
#gold (v4)
"#ffd700",\
#orange (v2)
"#ffaa5f",\
#light orange
"#ffae7c",\
#yellow-orange
"#ffca5f",\
#yellow (v1)
"#fff03a",\
#yellow (v2)
"#ebdf59",\
#yellow (v3)
"#f1e157",\
#pink orange
"#ff9a84",\
#indigo (v1)
"#c97fff",\
#indigo (v2)
"#6e76ff",\
]

# visual distance between various secondary colors
SECONDARY_COLOR_DISTANCE = {\
#turquoise:turquoise
"#01edd2:#01edd2":0,\
#turquoise:medium purple
"#01edd2:#c66aff":35,\
#turquoise:light electric pink (v1)
"#01edd2:#eb61ff":50,\
#turquoise:light electric pink (v2)
"#01edd2:#fc90ff":25,\
#turquoise:electric pink
"#01edd2:#f574ff":80,\
#turquoise:dark electric pink
"#01edd2:#ff60e1":85,\
#turquoise:coral
"#01edd2:#f88379":45,\
#turquoise:purple (v1)
"#01edd2:#977aff":55,\
#turquoise:purple (v2)
"#01edd2:#a971fc":65,\
#turquoise:purple (v3)
"#01edd2:#b76eff":60,\
#turquoise:purple (v4)
"#01edd2:#d985f7":40,\
#turquoise:purple (v5)
"#01edd2:#7f5fff":50,\
#turquoise:purple (v6)
"#01edd2:#a991ff":30,\
#turquoise:purple (v7)
"#01edd2:#a293ff":30,\
#turquoise:pink (v2)
"#01edd2:#ff7d9c":60,\
#turquoise:pink (v3)
"#01edd2:#fc98bc":40,\
#turquoise:reddish (v1)
"#01edd2:#ff5f5f":75,\
#turquoise:reddish (v2)
"#01edd2:#ff5a5a":80,\
#turquoise:tomato
"#01edd2:#ff8282":55,\
#turquoise:greenish yellow
"#01edd2:#d4d900":65,\
#turquoise:greenish
"#01edd2:#c8ff28":35,\
#turquoise:aquamarine (v1)
"#01edd2:#28ffaa":10,\
#turquoise:aquamarine (v2)
"#01edd2:#00eccb":1,\
#turquoise:firozi (v2)
"#01edd2:#2ff6ea":5,\
#turquoise:firozi (v3)
"#01edd2:#49d9ff":7,\
#turquoise:firozi (v4)
"#01edd2:#31e6ed":1,\
#turquoise:dull green
"#01edd2:#89e46c":25,\
#turquoise:mint greenish
"#01edd2:#9de245":30,\
#turquoise:mint green
"#01edd2:#66ff3a":30,\
#turquoise:light mint green
"#01edd2:#00f0a9":5,\
#turquoise:light green
"#01edd2:#a5ed31":20,\
#turquoise:green (v2)
"#01edd2:#2ff06f":15,\
#turquoise:green (v3)
"#01edd2:#26e99c":5,\
#turquoise:green (v4)
"#01edd2:#42ec72":10,\
#turquoise:green (v5)
"#01edd2:#46ec5c":10,\
#turquoise:green (v6)
"#01edd2:#50f777":7,\
#turquoise:green (v7)
"#01edd2:#01f5a1":5,\
#turquoise:green (v8)
"#01edd2:#42e966":10,\
#turquoise:green (v9)
"#01edd2:#52f578":10,\
#turquoise:sky blue (v1)
"#01edd2:#69baf5":10,\
#turquoise:sky blue (v2)
"#01edd2:#6d9eff":15,\
#turquoise:sky blue (v3)
"#01edd2:#32a8f8":25,\
#turquoise:sky blue (v4)
"#01edd2:#5caeff":15,\
#turquoise:sky blue (v5)
"#01edd2:#7ba6fc":15,\
#turquoise:blue
"#01edd2:#6292ff":20,\
#turquoise:sky-teal-blue
"#01edd2:#28d7ff":7,\
#turquoise:purple blue
"#01edd2:#9380ff":35,\
#turquoise:teal-blue (v1)
"#01edd2:#3bc1f0":7,\
#turquoise:teal-blue (v2)
"#01edd2:#34caf0":7,\
#turquoise:teal-blue (v3)
"#01edd2:#01b0ed":15,\
#turquoise:gold (v2)
"#01edd2:#f9cd48":35,\
#turquoise:gold (v3)
"#01edd2:#fed940":30,\
#turquoise:gold (v4)
"#01edd2:#ffd700":55,\
#turquoise:orange (v2)
"#01edd2:#ffaa5f":45,\
#turquoise:light orange
"#01edd2:#ffae7c":35,\
#turquoise:yellow-orange
"#01edd2:#ffca5f":40,\
#turquoise:yellow (v1)
"#01edd2:#fff03a":30,\
#turquoise:yellow (v2)
"#01edd2:#ebdf59":35,\
#turquoise:yellow (v3)
"#01edd2:#f1e157":35,\
#turquoise:pink orange
"#01edd2:#ff9a84":55,\
#turquoise:indigo (v1)
"#01edd2:#c97fff":70,\
#turquoise:indigo (v2)
"#01edd2:#6e76ff":40,\

#medium purple:turquoise
"#c66aff:#01edd2":35,\
#medium purple:medium purple
"#c66aff:#c66aff":0,\
#medium purple:light electric pink (v1)
"#c66aff:#eb61ff":7,\
#medium purple:light electric pink (v2)
"#c66aff:#fc90ff":7,\
#medium purple:electric pink
"#c66aff:#f574ff":5,\
#medium purple:dark electric pink
"#c66aff:#ff60e1":7,\
#medium purple:coral
"#c66aff:#f88379":20,\
#medium purple:purple (v1)
"#c66aff:#977aff":10,\
#medium purple:purple (v2)
"#c66aff:#a971fc":1,\
#medium purple:purple (v3)
"#c66aff:#b76eff":1,\
#medium purple:purple (v4)
"#c66aff:#d985f7":5,\
#medium purple:purple (v5)
"#c66aff:#7f5fff":15,\
#medium purple:purple (v6)
"#c66aff:#a991ff":5,\
#medium purple:purple (v7)
"#c66aff:#a293ff":5,\
#medium purple:pink (v2)
"#c66aff:#ff7d9c":30,\
#medium purple:pink (v3)
"#c66aff:#fc98bc":20,\
#medium purple:reddish (v1)
"#c66aff:#ff5f5f":50,\
#medium purple:reddis (v2)
"#c66aff:#ff5a5a":50,\
#medium purple:tomato
"#c66aff:#ff8282":30,\
#medium purple:greenish yellow
"#c66aff:#d4d900":65,\
#medium purple:greenish
"#c66aff:#c8ff28":60,\
#medium purple:aquamarine (v1)
"#c66aff:#28ffaa":70,\
#medium purple:aquamarine (v2)
"#c66aff:#00eccb":75,\
#medium purple:firozi (v2)
"#c66aff:#2ff6ea":70,\
#medium purple:firozi (v3)
"#c66aff:#49d9ff":50,\
#medium purple:firozi (v4)
"#c66aff:#31e6ed":55,\
#medium purple:dull green
"#c66aff:#89e46c":65,\
#medium purple:mint greenish
"#c66aff:#9de245":70,\
#medium purple:mint green
"#c66aff:#66ff3a":80,\
#medium purple:light mint green
"#c66aff:#00f0a9":80,\
#medium purple:light green
"#c66aff:#a5ed31":70,\
#medium purple:green (v2)
"#c66aff:#2ff06f":75,\
#medium purple:green (v3)
"#c66aff:#26e99c":65,\
#medium purple:green (v4)
"#c66aff:#42ec72":70,\
#medium purple:green (v5)
"#c66aff:#46ec5c":70,\
#medium purple:green (v6)
"#c66aff:#50f777":60,\
#medium purple:green (v7)
"#c66aff:#01f5a1":80,\
#medium purple:green (v8)
"#c66aff:#42e966":70,\
#medium purple:green (v9)
"#c66aff:#52f578":55,\
#medium purple:sky blue (v1)
"#c66aff:#69baf5":20,\
#medium purple:sky blue (v2)
"#c66aff:#6d9eff":15,\
#medium purple:sky blue (v3)
"#c66aff:#32a8f8":20,\
#medium purple:sky blue (v4)
"#c66aff:#5caeff":20,\
#medium purple:sky blue (v5)
"#c66aff:#7ba6fc":15,\
#medium purple:blue
"#c66aff:#6292ff":15,\
#medium purple:sky-teal-blue
"#c66aff:#28d7ff":25,\
#medium purple:purple blue
"#c66aff:#9380ff":5,\
#medium purple:teal-blue (v1)
"#c66aff:#3bc1f0":20,\
#medium purple:teal-blue (v2)
"#c66aff:#34caf0":20,\
#medium purple:teal-blue (v3)
"#c66aff:#01b0ed":50,\
#medium purple:gold (v2)
"#c66aff:#f9cd48":75,\
#medium purple:gold (v3)
"#c66aff:#fed940":75,\
#medium purple:gold (v4)
"#c66aff:#ffd700":80,\
#medium purple:orange (v2)
"#c66aff:#ffaa5f":60,\
#medium purple:light orange
"#c66aff:#ffae7c":55,\
#medium purple:yellow-orange
"#c66aff:#ffca5f":65,\
#medium purple:yellow (v1)
"#c66aff:#fff03a":70,\
#medium purple:yellow (v2)
"#c66aff:#ebdf59":75,\
#medium purple:yellow (v3)
"#c66aff:#f1e157":75,\
#medium purple:pink orange
"#c66aff:#ff9a84":35,\
#medium purple:indigo (v1)
"#c66aff:#c97fff":1,\
#medium purple:indigo (v2)
"#c66aff:#6e76ff":7,\

#light electric pink (v1):turquoise
"#eb61ff:#01edd2":50,\
#light electric pink (v1):medium purple
"#eb61ff:#c66aff":7,\
#light electric pink (v1):light electric pink (v1)
"#eb61ff:#eb61ff":0,\
#light electric pink (v1):light electric pink (v2)
"#eb61ff:#fc90ff":5,\
#light electric pink (v1):electric pink
"#eb61ff:#f574ff":1,\
#light electric pink (v1):dark electric pink
"#eb61ff:#ff60e1":5,\
#light electric pink (v1):coral
"#eb61ff:#f88379":15,\
#light electric pink (v1):purple (v1)
"#eb61ff:#977aff":10,\
#light electric pink (v1):purple (v2)
"#eb61ff:#a971fc":10,\
#light electric pink (v1):purple (v3)
"#eb61ff:#b76eff":5,\
#light electric pink (v1):purple (v4)
"#eb61ff:#d985f7":1,\
#light electric pink (v1):purple (v5)
"#eb61ff:#7f5fff":15,\
#light electric pink (v1):purple (v6)
"#eb61ff:#a991ff":10,\
#light electric pink (v1):purple (v7)
"#eb61ff:#a293ff":10,\
#light electric pink (v1):pink (v2)
"#eb61ff:#ff7d9c":15,\
#light electric pink (v1):pink (v3)
"#eb61ff:#fc98bc":10,\
#light electric pink (v1):reddish (v1)
"#eb61ff:#ff5f5f":25,\
#light electric pink (v1):reddis (v2)
"#eb61ff:#ff5a5a":25,\
#light electric pink (v1):tomato
"#eb61ff:#ff8282":15,\
#light electric pink (v1):greenish yellow
"#eb61ff:#d4d900":60,\
#light electric pink (v1):greenish
"#eb61ff:#c8ff28":50,\
#light electric pink (v1):aquamarine (v1)
"#eb61ff:#28ffaa":60,\
#light electric pink (v1):aquamarine (v2)
"#eb61ff:#00eccb":40,\
#light electric pink (v1):firozi (v2)
"#eb61ff:#2ff6ea":45,\
#light electric pink (v1):firozi (v3)
"#eb61ff:#49d9ff":30,\
#light electric pink (v1):firozi (v4)
"#eb61ff:#31e6ed":35,\
#light electric pink (v1):dull green
"#eb61ff:#89e46c":25,\
#light electric pink (v1):mint greenish
"#eb61ff:#9de245":45,\
#light electric pink (v1):mint green
"#eb61ff:#66ff3a":70,\
#light electric pink (v1):light mint green
"#eb61ff:#00f0a9":75,\
#light electric pink (v1):light green
"#eb61ff:#a5ed31":55,\
#light electric pink (v1):green (v2)
"#eb61ff:#2ff06f":65,\
#light electric pink (v1):green (v3)
"#eb61ff:#26e99c":45,\
#light electric pink (v1):green (v4)
"#eb61ff:#42ec72":55,\
#light electric pink (v1):green (v5)
"#eb61ff:#46ec5c":55,\
#light electric pink (v1):green (v6)
"#eb61ff:#50f777":35,\
#light electric pink (v1):green (v7)
"#eb61ff:#01f5a1":75,\
#light electric pink (v1):green (v8)
"#eb61ff:#42e966":65,\
#light electric pink (v1):green (v9)
"#eb61ff:#52f578":50,\
#light electric pink (v1):sky blue (v1)
"#eb61ff:#69baf5":25,\
#light electric pink (v1):sky blue (v2)
"#eb61ff:#6d9eff":20,\
#light electric pink (v1):sky blue (v3)
"#eb61ff:#32a8f8":35,\
#light electric pink (v1):sky blue (v4)
"#eb61ff:#5caeff":20,\
#light electric pink (v1):sky blue (v5)
"#eb61ff:#7ba6fc":15,\
#light electric pink (v1):blue
"#eb61ff:#6292ff":25,\
#light electric pink (v1):sky-teal-blue
"#eb61ff:#28d7ff":35,\
#light electric pink (v1):purple blue
"#eb61ff:#9380ff":10,\
#light electric pink (v1):teal-blue (v1)
"#eb61ff:#3bc1f0":25,\
#light electric pink (v1):teal-blue (v2)
"#eb61ff:#34caf0":25,\
#light electric pink (v1):teal-blue (v3)
"#eb61ff:#01b0ed":30,\
#light electric pink (v1):gold (v2)
"#eb61ff:#f9cd48":70,\
#light electric pink (v1):gold (v3)
"#eb61ff:#fed940":75,\
#light electric pink (v1):gold (v4)
"#eb61ff:#ffd700":80,\
#light electric pink (v1):orange (v2)
"#eb61ff:#ffaa5f":50,\
#light electric pink (v1):light orange
"#eb61ff:#ffae7c":40,\
#light electric pink (v1):yellow-orange
"#eb61ff:#ffca5f":45,\
#light electric pink (v1):yellow (v1)
"#eb61ff:#fff03a":35,\
#light electric pink (v1):yellow (v2)
"#eb61ff:#ebdf59":45,\
#light electric pink (v1):yellow (v3)
"#eb61ff:#f1e157":45,\
#light electric pink (v1):pink orange
"#eb61ff:#ff9a84":25,\
#light electric pink (v1):indigo (v1)
"#eb61ff:#c97fff":5,\
#light electric pink (v1):indigo (v2)
"#eb61ff:#6e76ff":20,\

#light electric pink (v2):turquoise
"#fc90ff:#01edd2":25,\
#light electric pink (v2):medium purple
"#fc90ff:#c66aff":7,\
#light electric pink (v2):light electric pink (v1)
"#fc90ff:#eb61ff":5,\
#light electric pink (v2):light electric pink (v2)
"#fc90ff:#fc90ff":0,\
#light electric pink (v2):electric pink
"#fc90ff:#f574ff":1,\
#light electric pink (v2):dark electric pink
"#fc90ff:#ff60e1":5,\
#light electric pink (v2):coral
"#fc90ff:#f88379":10,\
#light electric pink (v2):purple (v1)
"#fc90ff:#977aff":10,\
#light electric pink (v2):purple (v2)
"#fc90ff:#a971fc":10,\
#light electric pink (v2):purple (v3)
"#fc90ff:#b76eff":5,\
#light electric pink (v2):purple (v4)
"#fc90ff:#d985f7":1,\
#light electric pink (v2):purple (v5)
"#fc90ff:#7f5fff":15,\
#light electric pink (v2):purple (v6)
"#fc90ff:#a991ff":7,\
#light electric pink (v2):purple (v7)
"#fc90ff:#a293ff":7,\
#light electric pink (v2):pink (v2)
"#fc90ff:#ff7d9c":10,\
#light electric pink (v2):pink (v3)
"#fc90ff:#fc98bc":5,\
#light electric pink (v2):reddish (v1)
"#fc90ff:#ff5f5f":20,\
#light electric pink (v2):reddish (v2)
"#fc90ff:#ff5a5a":20,\
#light electric pink (v2):tomato
"#fc90ff:#ff8282":10,\
#light electric pink (v2):greenish yellow
"#fc90ff:#d4d900":70,\
#light electric pink (v2):greenish
"#fc90ff:#c8ff28":40,\
#light electric pink (v2):aquamarine (v1)
"#fc90ff:#28ffaa":30,\
#light electric pink (v2):aquamarine (v2)
"#fc90ff:#00eccb":45,\
#light electric pink (v2):firozi (v2)
"#fc90ff:#2ff6ea":30,\
#light electric pink (v2):firozi (v3)
"#fc90ff:#49d9ff":35,\
#light electric pink (v2):firozi (v4)
"#fc90ff:#31e6ed":35,\
#light electric pink (v2):dull green
"#fc90ff:#89e46c":25,\
#light electric pink (v2):mint greenish
"#fc90ff:#9de245":30,\
#light electric pink (v2):mint green
"#fc90ff:#66ff3a":65,\
#light electric pink (v2):light mint green
"#fc90ff:#00f0a9":55,\
#light electric pink (v2):light green
"#fc90ff:#a5ed31":60,\
#light electric pink (v2):green (v2)
"#fc90ff:#2ff06f":70,\
#light electric pink (v2):green (v3)
"#fc90ff:#26e99c":50,\
#light electric pink (v2):green (v4)
"#fc90ff:#42ec72":55,\
#light electric pink (v2):green (v5)
"#fc90ff:#46ec5c":55,\
#light electric pink (v2):green (v6)
"#fc90ff:#50f777":40,\
#light electric pink (v2):green (v7)
"#fc90ff:#01f5a1":45,\
#light electric pink (v2):green (v8)
"#fc90ff:#42e966":55,\
#light electric pink (v2):green (v9)
"#fc90ff:#52f578":40,\
#light electric pink (v2):sky blue (v1)
"#fc90ff:#69baf5":20,\
#light electric pink (v2):sky blue (v2)
"#fc90ff:#6d9eff":25,\
#light electric pink (v2):sky blue (v3)
"#fc90ff:#32a8f8":35,\
#light electric pink (v2):sky blue (v4)
"#fc90ff:#5caeff":25,\
#light electric pink (v2):sky blue (v5)
"#fc90ff:#7ba6fc":15,\
#light electric pink (v2):blue
"#fc90ff:#6292ff":20,\
#light electric pink (v2):sky-teal-blue
"#fc90ff:#28d7ff":30,\
#light electric pink (v2):purple blue
"#fc90ff:#9380ff":10,\
#light electric pink (v2):teal-blue (v1)
"#fc90ff:#3bc1f0":20,\
#light electric pink (v2):teal-blue (v2)
"#fc90ff:#34caf0":20,\
#light electric pink (v2):teal-blue (v3)
"#fc90ff:#01b0ed":35,\
#light electric pink (v2):gold (v2)
"#fc90ff:#f9cd48":55,\
#light electric pink (v2):gold (v3)
"#fc90ff:#fed940":55,\
#light electric pink (v2):gold (v4)
"#fc90ff:#ffd700":65,\
#light electric pink (v2):orange (v2)
"#fc90ff:#ffaa5f":30,\
#light electric pink (v2):light orange
"#fc90ff:#ffae7c":25,\
#light electric pink (v2):yellow-orange
"#fc90ff:#ffca5f":30,\
#light electric pink (v2):yellow (v1)
"#fc90ff:#fff03a":20,\
#light electric pink (v2):yellow (v2)
"#fc90ff:#ebdf59":30,\
#light electric pink (v2):yellow (v3)
"#fc90ff:#f1e157":30,\
#light electric pink (v2):pink orange
"#fc90ff:#ff9a84":15,\
#light electric pink (v2):indigo (v1)
"#fc90ff:#c97fff":5,\
#light electric pink (v2):indigo (v2)
"#fc90ff:#6e76ff":25,\

#electric pink:turquoise
"#f574ff:#01edd2":80,\
#electric pink:medium purple
"#f574ff:#c66aff":5,\
#electric pink:light electric pink (v1)
"#f574ff:#eb61ff":1,\
#electric pink:light electric pink (v2)
"#f574ff:#fc90ff":1,\
#electric pink:electric pink
"#f574ff:#f574ff":0,\
#electric pink:dark electric pink
"#f574ff:#ff60e1":3,\
#electric pink:coral
"#f574ff:#f88379":10,\
#electric pink:purple (v1)
"#f574ff:#977aff":10,\
#electric pink:purple (v2)
"#f574ff:#a971fc":7,\
#electric pink:purple (v3)
"#f574ff:#b76eff":5,\
#electric pink:purple (v4)
"#f574ff:#d985f7":1,\
#electric pink:purple (v5)
"#f574ff:#7f5fff":15,\
#electric pink:purple (v6)
"#f574ff:#a991ff":7,\
#electric pink:purple (v7)
"#f574ff:#a293ff":7,\
#electric pink:pink (v2)
"#f574ff:#ff7d9c":10,\
#electric pink:pink (v3)
"#f574ff:#fc98bc":5,\
#electric pink:reddish (v1)
"#f574ff:#ff5f5f":17,\
#electric pink:reddish (v2)
"#f574ff:#ff5a5a":18,\
#electric pink:tomato
"#f574ff:#ff8282":10,\
#electric pink:greenish yellow
"#f574ff:#d4d900":65,\
#electric pink:greenish
"#f574ff:#c8ff28":55,\
#electric pink:aquamarine (v1)
"#f574ff:#28ffaa":60,\
#electric pink:aquamarine (v2)
"#f574ff:#00eccb":70,\
#electric pink:firozi (v2)
"#f574ff:#2ff6ea":55,\
#electric pink:firozi (v3)
"#f574ff:#49d9ff":40,\
#electric pink:firozi (v4)
"#f574ff:#31e6ed":50,\
#electric pink:dull green
"#f574ff:#89e46c":45,\
#electric pink:mint greenish
"#f574ff:#9de245":50,\
#electric pink:mint green
"#f574ff:#66ff3a":70,\
#electric pink:light mint green
"#f574ff:#00f0a9":60,\
#electric pink:light green
"#f574ff:#a5ed31":65,\
#electric pink:green (v2)
"#f574ff:#2ff06f":40,\
#electric pink:green (v3)
"#f574ff:#26e99c":30,\
#electric pink:green (v4)
"#f574ff:#42ec72":30,\
#electric pink:green (v5)
"#f574ff:#46ec5c":35,\
#electric pink:green (v6)
"#f574ff:#50f777":25,\
#electric pink:green (v7)
"#f574ff:#01f5a1":55,\
#electric pink:green (v8)
"#f574ff:#42e966":55,\
#electric pink:green (v9)
"#f574ff:#52f578":40,\
#electric pink:sky blue (v1)
"#f574ff:#69baf5":25,\
#electric pink:sky blue (v2)
"#f574ff:#6d9eff":20,\
#electric pink:sky blue (v3)
"#f574ff:#32a8f8":30,\
#electric pink:sky blue (v4)
"#f574ff:#5caeff":20,\
#electric pink:sky blue (v5)
"#f574ff:#7ba6fc":15,\
#electric pink:blue
"#f574ff:#6292ff":30,\
#electric pink:sky-teal-blue
"#f574ff:#28d7ff":75,\
#electric pink:purple blue
"#f574ff:#9380ff":10,\
#electric pink:teal-blue (v1)
"#f574ff:#3bc1f0":40,\
#electric pink:teal-blue (v2)
"#f574ff:#34caf0":40,\
#electric pink:teal-blue (v3)
"#f574ff:#01b0ed":50,\
#electric pink:gold (v2)
"#f574ff:#f9cd48":65,\
#electric pink:gold (v3)
"#f574ff:#fed940":60,\
#electric pink:gold (v4)
"#f574ff:#ffd700":80,\
#electric pink:orange (v2)
"#f574ff:#ffaa5f":50,\
#electric pink:light orange
"#f574ff:#ffae7c":40,\
#electric pink:yellow-orange
"#f574ff:#ffca5f":30,\
#electric pink:yellow (v1)
"#f574ff:#fff03a":20,\
#electric pink:yellow (v2)
"#f574ff:#ebdf59":30,\
#electric pink:yellow (v3)
"#f574ff:#f1e157":30,\
#electric pink:pink orange
"#f574ff:#ff9a84":15,\
#electric pink:indigo (v1)
"#f574ff:#c97fff":5,\
#electric pink:indigo (v2)
"#f574ff:#6e76ff":10,\

#dark electric pink:turquoise
"#ff60e1:#01edd2":85,\
#dark electric pink:medium purple
"#ff60e1:#c66aff":7,\
#dark electric pink:light electric pink (v1)
"#ff60e1:#eb61ff":5,\
#dark electric pink:light electric pink (v2)
"#ff60e1:#fc90ff":5,\
#dark electric pink:electric pink
"#ff60e1:#f574ff":3,\
#dark electric pink:dark electric pink
"#ff60e1:#ff60e1":0,\
#dark electric pink:coral
"#ff60e1:#f88379":10,\
#dark electric pink:purple (v1)
"#ff60e1:#977aff":11,\
#dark electric pink:purple (v2)
"#ff60e1:#a971fc":10,\
#dark electric pink:purple (v3)
"#ff60e1:#b76eff":7,\
#dark electric pink:purple (v4)
"#ff60e1:#d985f7":5,\
#dark electric pink:purple (v5)
"#ff60e1:#7f5fff":15,\
#dark electric pink:purple (v6)
"#ff60e1:#a991ff":7,\
#dark electric pink:purple (v7)
"#ff60e1:#a293ff":7,\
#dark electric pink:pink (v2)
"#ff60e1:#ff7d9c":7,\
#dark electric pink:pink (v3)
"#ff60e1:#fc98bc":5,\
#dark electric pink:reddish (v1)
"#ff60e1:#ff5f5f":15,\
#dark electric pink:reddish (v2)
"#ff60e1:#ff5a5a":15,\
#dark electric pink:tomato
"#ff60e1:#ff8282":10,\
#dark electric pink:greenish yellow
"#ff60e1:#d4d900":50,\
#dark electric pink:greenish
"#ff60e1:#c8ff28":55,\
#dark electric pink:aquamarine (v1)
"#ff60e1:#28ffaa":45,\
#dark electric pink:aquamarine (v2)
"#ff60e1:#00eccb":40,\
#dark electric pink:firozi (v2)
"#ff60e1:#2ff6ea":35,\
#dark electric pink:firozi (v3)
"#ff60e1:#49d9ff":30,\
#dark electric pink:firozi (v4)
"#ff60e1:#31e6ed":35,\
#dark electric pink:dull green
"#ff60e1:#89e46c":30,\
#dark electric pink:mint greenish
"#ff60e1:#9de245":35,\
#dark electric pink:mint green
"#ff60e1:#66ff3a":55,\
#dark electric pink:light mint green
"#ff60e1:#00f0a9":45,\
#dark electric pink:light green
"#ff60e1:#a5ed31":40,\
#dark electric pink:green (v2)
"#ff60e1:#2ff06f":40,\
#dark electric pink:green (v3)
"#ff60e1:#26e99c":35,\
#dark electric pink:green (v4)
"#ff60e1:#42ec72":35,\
#dark electric pink:green (v5)
"#ff60e1:#46ec5c":40,\
#dark electric pink:green (v6)
"#ff60e1:#50f777":30,\
#dark electric pink:green (v7)
"#ff60e1:#01f5a1":45,\
#dark electric pink:green (v8)
"#ff60e1:#42e966":40,\
#dark electric pink:green (v9)
"#ff60e1:#52f578":25,\
#dark electric pink:sky blue (v1)
"#ff60e1:#69baf5":30,\
#dark electric pink:sky blue (v2)
"#ff60e1:#6d9eff":40,\
#dark electric pink:sky blue (v3)
"#ff60e1:#32a8f8":50,\
#dark electric pink:sky blue (v4)
"#ff60e1:#5caeff":40,\
#dark electric pink:sky blue (v5)
"#ff60e1:#7ba6fc":25,\
#dark electric pink:blue
"#ff60e1:#6292ff":35,\
#dark electric pink:sky-teal-blue
"#ff60e1:#28d7ff":55,\
#dark electric pink:purple blue
"#ff60e1:#9380ff":15,\
#dark electric pink:teal-blue (v1)
"#ff60e1:#3bc1f0":35,\
#dark electric pink:teal-blue (v2)
"#ff60e1:#34caf0":35,\
#dark electric pink:teal-blue (v3)
"#ff60e1:#01b0ed":60,\
#dark electric pink:gold (v2)
"#ff60e1:#f9cd48":55,\
#dark electric pink:gold (v3)
"#ff60e1:#fed940":55,\
#dark electric pink:gold (v4)
"#ff60e1:#ffd700":80,\
#dark electric pink:orange (v2)
"#ff60e1:#ffaa5f":45,\
#dark electric pink:light orange
"#ff60e1:#ffae7c":40,\
#dark electric pink:yellow-orange
"#ff60e1:#ffca5f":45,\
#dark electric pink:yellow (v1)
"#ff60e1:#fff03a":35,\
#dark electric pink:yellow (v2)
"#ff60e1:#ebdf59":40,\
#dark electric pink:yellow (v3)
"#ff60e1:#f1e157":40,\
#dark electric pink:pink orange
"#ff60e1:#ff9a84":15,\
#dark electric pink:indigo (v1)
"#ff60e1:#c97fff":7,\
#dark electric pink:indigo (v2)
"#ff60e1:#6e76ff":20,\

#coral:turquoise
"#f88379:#01edd2":45,\
#coral:medium purple
"#f88379:#c66aff":20,\
#coral:light electric pink (v1)
"#f88379:#eb61ff":15,\
#coral:light electric pink (v2)
"#f88379:#fc90ff":10,\
#coral:electric pink
"#f88379:#f574ff":10,\
#coral:dark electric pink
"#f88379:#ff60e1":10,\
#coral:coral
"#f88379:#f88379":0,\
#coral:purple (v1)
"#f88379:#977aff":20,\
#coral:purple (v2)
"#f88379:#a971fc":20,\
#coral:purple (v3)
"#f88379:#b76eff":15,\
#coral:purple (v4)
"#f88379:#d985f7":10,\
#coral:purple (v5)
"#f88379:#7f5fff":30,\
#coral:purple (v6)
"#f88379:#a991ff":12,\
#coral:purple (v7)
"#f88379:#a293ff":12,\
#coral:pink (v2)
"#f88379:#ff7d9c":5,\
#coral:pink (v3)
"#f88379:#fc98bc":5,\
#coral:reddish (v1)
"#f88379:#ff5f5f":5,\
#coral:reddish (v2)
"#f88379:#ff5a5a":5,\
#coral:tomato
"#f88379:#ff8282":1,\
#coral:greenish yellow
"#f88379:#d4d900":25,\
#coral:greenish
"#f88379:#c8ff28":20,\
#coral:aquamarine (v1)
"#f88379:#28ffaa":40,\
#coral:aquamarine (v2)
"#f88379:#00eccb":45,\
#coral:firozi (v2)
"#f88379:#2ff6ea":35,\
#coral:firozi (v3)
"#f88379:#49d9ff":40,\
#coral:firozi (v4)
"#f88379:#31e6ed":50,\
#coral:dull green
"#f88379:#89e46c":25,\
#coral:mint greenish
"#f88379:#9de245":30,\
#coral:mint green
"#f88379:#66ff3a":45,\
#coral:light mint green
"#f88379:#00f0a9":45,\
#coral:light green
"#f88379:#a5ed31":25,\
#coral:green (v2)
"#f88379:#2ff06f":35,\
#coral:green (v3)
"#f88379:#26e99c":30,\
#coral:green (v4)
"#f88379:#42ec72":35,\
#coral:green (v5)
"#f88379:#46ec5c":35,\
#coral:green (v6)
"#f88379:#50f777":25,\
#coral:green (v7)
"#f88379:#01f5a1":40,\
#coral:green (v8)
"#f88379:#42e966":35,\
#coral:green (v9)
"#f88379:#52f578":25,\
#coral:sky blue (v1)
"#f88379:#69baf5":35,\
#coral:sky blue (v2)
"#f88379:#6d9eff":40,\
#coral:sky blue (v3)
"#f88379:#32a8f8":55,\
#coral:sky blue (v4)
"#f88379:#5caeff":40,\
#coral:sky blue (v5)
"#f88379:#7ba6fc":35,\
#coral:blue
"#f88379:#6292ff":45,\
#coral:sky-teal-blue
"#f88379:#28d7ff":55,\
#coral:purple blue
"#f88379:#9380ff":30,\
#coral:teal-blue (v1)
"#f88379:#3bc1f0":40,\
#coral:teal-blue (v2)
"#f88379:#34caf0":35,\
#coral:teal-blue (v3)
"#f88379:#01b0ed":50,\
#coral:gold (v2)
"#f88379:#f9cd48":25,\
#coral:gold (v3)
"#f88379:#fed940":25,\
#coral:gold (v4)
"#f88379:#ffd700":30,\
#coral:orange (v2)
"#f88379:#ffaa5f":10,\
#coral:light orange
"#f88379:#ffae7c":7,\
#coral:yellow-orange
"#f88379:#ffca5f":10,\
#coral:yellow (v1)
"#f88379:#fff03a":15,\
#coral:yellow (v2)
"#f88379:#ebdf59":20,\
#coral:yellow (v3)
"#f88379:#f1e157":20,\
#coral:pink orange
"#f88379:#ff9a84":1,\
#coral:indigo (v1)
"#f88379:#c97fff":30,\
#coral:indigo (v2)
"#f88379:#6e76ff":45,\

#purple (v1):turquoise
"#977aff:#01edd2":55,\
#purple (v1):medium purple
"#977aff:#c66aff":10,\
#purple (v1):light electric pink (v1)
"#977aff:#eb61ff":10,\
#purple (v1):light electric pink (v2)
"#977aff:#fc90ff":10,\
#purple (v1):electric pink
"#977aff:#f574ff":10,\
#purple (v1):dark electric pink
"#977aff:#ff60e1":11,\
#purple (v1):coral
"#977aff:#f88379":20,\
#purple (v1):purple (v1)
"#977aff:#977aff":0,\
#purple (v1):purple (v2)
"#977aff:#a971fc":3,\
#purple (v1):purple (v3)
"#977aff:#b76eff":5,\
#purple (v1):purple (v4)
"#977aff:#d985f7":7,\
#purple (v1):purple (v5)
"#977aff:#7f5fff":7,\
#purple (v1):purple (v6)
"#977aff:#a991ff":5,\
#purple (v1):purple (v7)
"#977aff:#a293ff":3,\
#purple (v1):pink (v2)
"#977aff:#ff7d9c":25,\
#purple (v1):pink (v3)
"#977aff:#fc98bc":15,\
#purple (v1):reddish (v1)
"#977aff:#ff5f5f":45,\
#purple (v1):reddis (v2)
"#977aff:#ff5a5a":45,\
#purple (v1):tomato
"#977aff:#ff8282":20,\
#purple (v1):greenish yellow
"#977aff:#d4d900":65,\
#purple (v1):greenish
"#977aff:#c8ff28":50,\
#purple (v1):aquamarine (v1)
"#977aff:#28ffaa":40,\
#purple (v1):aquamarine (v2)
"#977aff:#00eccb":35,\
#purple (v1):firozi (v2)
"#977aff:#2ff6ea":30,\
#purple (v1):firozi (v3)
"#977aff:#49d9ff":20,\
#purple (v1):firozi (v4)
"#977aff:#31e6ed":25,\
#purple (v1):dull green
"#977aff:#89e46c":30,\
#purple (v1):mint greenish
"#977aff:#9de245":35,\
#purple (v1):mint green
"#977aff:#66ff3a":45,\
#purple (v1):light mint green
"#977aff:#00f0a9":25,\
#purple (v1):light green
"#977aff:#a5ed31":35,\
#purple (v1):green (v2)
"#977aff:#2ff06f":30,\
#purple (v1):green (v3)
"#977aff:#26e99c":30,\
#purple (v1):green (v4)
"#977aff:#42ec72":35,\
#purple (v1):green (v5)
"#977aff:#46ec5c":35,\
#purple (v1):green (v6)
"#977aff:#50f777":25,\
#purple (v1):green (v7)
"#977aff:#01f5a1":30,\
#purple (v1):green (v8)
"#977aff:#42e966":35,\
#purple (v1):green (v9)
"#977aff:#52f578":20,\
#purple (v1):sky blue (v1)
"#977aff:#69baf5":7,\
#purple (v1):sky blue (v2)
"#977aff:#6d9eff":5,\
#purple (v1):sky blue (v3)
"#977aff:#32a8f8":10,\
#purple (v1):sky blue (v4)
"#977aff:#5caeff":7,\
#purple (v1):sky blue (v5)
"#977aff:#7ba6fc":5,\
#purple (v1):blue
"#977aff:#6292ff":5,\
#purple (v1):sky-teal-blue
"#977aff:#28d7ff":15,\
#purple (v1):purple blue
"#977aff:#9380ff":1,\
#purple (v1):teal-blue (v1)
"#977aff:#3bc1f0":15,\
#purple (v1):teal-blue (v2)
"#977aff:#34caf0":15,\
#purple (v1):teal-blue (v3)
"#977aff:#01b0ed":10,\
#purple (v1):gold (v2)
"#977aff:#f9cd48":55,\
#purple (v1):gold (v3)
"#977aff:#fed940":50,\
#purple (v1):gold (v4)
"#977aff:#ffd700":65,\
#purple (v1):orange (v2)
"#977aff:#ffaa5f":45,\
#purple (v1):light orange
"#977aff:#ffae7c":40,\
#purple (v1):yellow-orange
"#977aff:#ffca5f":35,\
#purple (v1):yellow (v1)
"#977aff:#fff03a":25,\
#purple (v1):yellow (v2)
"#977aff:#ebdf59":30,\
#purple (v1):yellow (v3)
"#977aff:#f1e157":30,\
#purple (v1):pink orange
"#977aff:#ff9a84":45,\
#purple (v1):indigo (v1)
"#977aff:#c97fff":5,\
#purple (v1):indigo (v2)
"#977aff:#6e76ff":1,\

#purple (v2):turquoise
"#a971fc:#01edd2":45,\
#purple (v2):medium purple
"#a971fc:#c66aff":1,\
#purple (v2):light electric pink (v1)
"#a971fc:#eb61ff":10,\
#purple (v2):light electric pink (v2)
"#a971fc:#fc90ff":10,\
#purple (v2):electric pink
"#a971fc:#f574ff":7,\
#purple (v2):dark electric pink
"#a971fc:#ff60e1":10,\
#purple (v2):coral
"#a971fc:#f88379":20,\
#purple (v2):purple (v1)
"#a971fc:#977aff":3,\
#purple (v2):purple (v2)
"#a971fc:#a971fc":0,\
#purple (v2):purple (v3)
"#a971fc:#b76eff":3,\
#purple (v2):purple (v4)
"#a971fc:#d985f7":7,\
#purple (v2):purple (v5)
"#a971fc:#7f5fff":7,\
#purple (v2):purple (v6)
"#a971fc:#a991ff":5,\
#purple (v2):purple (v7)
"#a971fc:#a293ff":5,\
#purple (v2):pink (v2)
"#a971fc:#ff7d9c":20,\
#purple (v2):pink (v3)
"#a971fc:#fc98bc":15,\
#purple (v2):reddish (v1)
"#a971fc:#ff5f5f":35,\
#purple (v2):reddis (v2)
"#a971fc:#ff5a5a":35,\
#purple (v2):tomato
"#a971fc:#ff8282":20,\
#purple (v2):greenish yellow
"#a971fc:#d4d900":55,\
#purple (v2):greenish
"#a971fc:#c8ff28":45,\
#purple (v2):aquamarine (v1)
"#a971fc:#28ffaa":30,\
#purple (v2):aquamarine (v2)
"#a971fc:#00eccb":25,\
#purple (v2):firozi (v2)
"#a971fc:#2ff6ea":30,\
#purple (v2):firozi (v3)
"#a971fc:#49d9ff":15,\
#purple (v2):firozi (v4)
"#a971fc:#31e6ed":20,\
#purple (v2):dull green
"#a971fc:#89e46c":35,\
#purple (v2):mint greenish
"#a971fc:#9de245":40,\
#purple (v2):mint green
"#a971fc:#66ff3a":50,\
#purple (v2):light mint green
"#a971fc:#00f0a9":35,\
#purple (v2):light green
"#a971fc:#a5ed31":45,\
#purple (v2):green (v2)
"#a971fc:#2ff06f":40,\
#purple (v2):green (v3)
"#a971fc:#26e99c":35,\
#purple (v2):green (v4)
"#a971fc:#42ec72":35,\
#purple (v2):green (v5)
"#a971fc:#46ec5c":35,\
#purple (v2):green (v6)
"#a971fc:#50f777":30,\
#purple (v2):green (v7)
"#a971fc:#01f5a1":25,\
#purple (v2):green (v8)
"#a971fc:#42e966":35,\
#purple (v2):green (v9)
"#a971fc:#52f578":30,\
#purple (v2):sky blue (v1)
"#a971fc:#69baf5":10,\
#purple (v2):sky blue (v2)
"#a971fc:#6d9eff":10,\
#purple (v2):sky blue (v3)
"#a971fc:#32a8f8":10,\
#purple (v2):sky blue (v4)
"#a971fc:#5caeff":7,\
#purple (v2):sky blue (v5)
"#a971fc:#7ba6fc":5,\
#purple (v2):blue
"#a971fc:#6292ff":7,\
#purple (v2):sky-teal-blue
"#a971fc:#28d7ff":15,\
#purple (v2):purple blue
"#a971fc:#9380ff":1,\
#purple (v2):teal-blue (v1)
"#a971fc:#3bc1f0":15,\
#purple (v2):teal-blue (v2)
"#a971fc:#34caf0":15,\
#purple (v2):teal-blue (v3)
"#a971fc:#01b0ed":20,\
#purple (v2):gold (v2)
"#a971fc:#f9cd48":70,\
#purple (v2):gold (v3)
"#a971fc:#fed940":75,\
#purple (v2):gold (v4)
"#a971fc:#ffd700":85,\
#purple (v2):orange (v2)
"#a971fc:#ffaa5f":60,\
#purple (v2):light orange
"#a971fc:#ffae7c":55,\
#purple (v2):yellow-orange
"#a971fc:#ffca5f":45,\
#purple (v2):yellow (v1)
"#a971fc:#fff03a":30,\
#purple (v2):yellow (v2)
"#a971fc:#ebdf59":35,\
#purple (v2):yellow (v3)
"#a971fc:#f1e157":35,\
#purple (v2):pink orange
"#a971fc:#ff9a84":45,\
#purple (v2):indigo (v1)
"#a971fc:#c97fff":5,\
#purple (v2):indigo (v2)
"#a971fc:#6e76ff":5,\

#purple (v3):turquoise
"#b76eff:#01edd2":60,\
#purple (v3):medium purple
"#b76eff:#c66aff":1,\
#purple (v3):light electric pink (v1)
"#b76eff:#eb61ff":5,\
#purple (v3):light electric pink (v2)
"#b76eff:#fc90ff":5,\
#purple (v3):electric pink
"#b76eff:#f574ff":5,\
#purple (v3):dark electric pink
"#b76eff:#ff60e1":7,\
#purple (v3):coral
"#b76eff:#f88379":15,\
#purple (v3):purple (v1)
"#b76eff:#977aff":5,\
#purple (v3):purple (v2)
"#b76eff:#a971fc":3,\
#purple (v3):purple (v3)
"#b76eff:#b76eff":0,\
#purple (v3):purple (v4)
"#b76eff:#d985f7":5,\
#purple (v3):purple (v5)
"#b76eff:#7f5fff":10,\
#purple (v3):purple (v6)
"#b76eff:#a991ff":1,\
#purple (v3):purple (v7)
"#b76eff:#a293ff":1,\
#purple (v3):pink (v2)
"#b76eff:#ff7d9c":20,\
#purple (v3):pink (v3)
"#b76eff:#fc98bc":15,\
#purple (v3):reddish (v1)
"#b76eff:#ff5f5f":35,\
#purple (v3):reddish (v2)
"#b76eff:#ff5a5a":35,\
#purple (v3):tomato
"#b76eff:#ff8282":15,\
#purple (v3):greenish yellow
"#b76eff:#d4d900":60,\
#purple (v3):greenish
"#b76eff:#c8ff28":40,\
#purple (v3):aquamarine (v1)
"#b76eff:#28ffaa":30,\
#purple (v3):aquamarine (v2)
"#b76eff:#00eccb":35,\
#purple (v3):firozi (v2)
"#b76eff:#2ff6ea":25,\
#purple (v3):firozi (v3)
"#b76eff:#49d9ff":20,\
#purple (v3):firozi (v4)
"#b76eff:#31e6ed":25,\
#purple (v3):dull green
"#b76eff:#89e46c":35,\
#purple (v3):mint greenish
"#b76eff:#9de245":40,\
#purple (v3):mint green
"#b76eff:#66ff3a":55,\
#purple (v3):light mint green
"#b76eff:#00f0a9":45,\
#purple (v3):light green
"#b76eff:#a5ed31":50,\
#purple (v3):green (v2)
"#b76eff:#2ff06f":40,\
#purple (v3):green (v3)
"#b76eff:#26e99c":35,\
#purple (v3):green (v4)
"#b76eff:#42ec72":35,\
#purple (v3):green (v5)
"#b76eff:#46ec5c":35,\
#purple (v3):green (v6)
"#b76eff:#50f777":30,\
#purple (v3):green (v7)
"#b76eff:#01f5a1":35,\
#purple (v3):green (v8)
"#b76eff:#42e966":35,\
#purple (v3):green (v9)
"#b76eff:#52f578":30,\
#purple (v3):sky blue (v1)
"#b76eff:#69baf5":15,\
#purple (v3):sky blue (v2)
"#b76eff:#6d9eff":10,\
#purple (v3):sky blue (v3)
"#b76eff:#32a8f8":20,\
#purple (v3):sky blue (v4)
"#b76eff:#5caeff":15,\
#purple (v3):sky blue (v5)
"#b76eff:#7ba6fc":10,\
#purple (v3):blue
"#b76eff:#6292ff":10,\
#purple (v3):sky-teal-blue
"#b76eff:#28d7ff":15,\
#purple (v3):purple blue
"#b76eff:#9380ff":1,\
#purple (v3):teal-blue (v1)
"#b76eff:#3bc1f0":20,\
#purple (v3):teal-blue (v2)
"#b76eff:#34caf0":20,\
#purple (v3):teal-blue (v3)
"#b76eff:#01b0ed":25,\
#purple (v3):gold (v2)
"#b76eff:#f9cd48":65,\
#purple (v3):gold (v3)
"#b76eff:#fed940":60,\
#purple (v3):gold (v4)
"#b76eff:#ffd700":70,\
#purple (v3):orange (v2)
"#b76eff:#ffaa5f":55,\
#purple (v3):light orange
"#b76eff:#ffae7c":50,\
#purple (v3):yellow-orange
"#b76eff:#ffca5f":45,\
#purple (v3):yellow (v1)
"#b76eff:#fff03a":60,\
#purple (v3):yellow (v2)
"#b76eff:#ebdf59":40,\
#purple (v3):yellow (v3)
"#b76eff:#f1e157":40,\
#purple (v3):pink orange
"#b76eff:#ff9a84":35,\
#purple (v3):indigo (v1)
"#b76eff:#c97fff":1,\
#purple (v3):indigo (v2)
"#b76eff:#6e76ff":10,\

#purple (v4):turquoise
"#d985f7:#01edd2":40,\
#purple (v4):medium purple
"#d985f7:#c66aff":5,\
#purple (v4):light electric pink (v1)
"#d985f7:#eb61ff":1,\
#purple (v4):light electric pink (v2)
"#d985f7:#fc90ff":1,\
#purple (v4):electric pink
"#d985f7:#f574ff":1,\
#purple (v4):dark electric pink
"#d985f7:#ff60e1":5,\
#purple (v4):coral
"#d985f7:#f88379":10,\
#purple (v4):purple (v1)
"#d985f7:#977aff":7,\
#purple (v4):purple (v2)
"#d985f7:#a971fc":7,\
#purple (v4):purple (v3)
"#d985f7:#b76eff":5,\
#purple (v4):purple (v4)
"#d985f7:#d985f7":0,\
#purple (v4):purple (v5)
"#d985f7:#7f5fff":15,\
#purple (v4):purple (v6)
"#d985f7:#a991ff":10,\
#purple (v4):purple (v7)
"#d985f7:#a293ff":10,\
#purple (v4):pink (v2)
"#d985f7:#ff7d9c":15,\
#purple (v4):pink (v3)
"#d985f7:#fc98bc":10,\
#purple (v4):reddish (v1)
"#d985f7:#ff5f5f":30,\
#purple (v4):reddis (v2)
"#d985f7:#ff5a5a":30,\
#purple (v4):tomato
"#d985f7:#ff8282":20,\
#purple (v4):greenish yellow
"#d985f7:#d4d900":45,\
#purple (v4):greenish
"#d985f7:#c8ff28":25,\
#purple (v4):aquamarine (v1)
"#d985f7:#28ffaa":35,\
#purple (v4):aquamarine (v2)
"#d985f7:#00eccb":45,\
#purple (v4):firozi (v2)
"#d985f7:#2ff6ea":35,\
#purple (v4):firozi (v3)
"#d985f7:#49d9ff":40,\
#purple (v4):firozi (v4)
"#d985f7:#31e6ed":45,\
#purple (v4):dull green
"#d985f7:#89e46c":25,\
#purple (v4):mint greenish
"#d985f7:#9de245":30,\
#purple (v4):mint green
"#d985f7:#66ff3a":50,\
#purple (v4):light mint green
"#d985f7:#00f0a9":45,\
#purple (v4):light green
"#d985f7:#a5ed31":50,\
#purple (v4):green (v2)
"#d985f7:#2ff06f":45,\
#purple (v4):green (v3)
"#d985f7:#26e99c":40,\
#purple (v4):green (v4)
"#d985f7:#42ec72":45,\
#purple (v4):green (v5)
"#d985f7:#46ec5c":50,\
#purple (v4):green (v6)
"#d985f7:#50f777":45,\
#purple (v4):green (v7)
"#d985f7:#01f5a1":50,\
#purple (v4):green (v8)
"#d985f7:#42e966":55,\
#purple (v4):green (v9)
"#d985f7:#52f578":45,\
#purple (v4):sky blue (v1)
"#d985f7:#69baf5":35,\
#purple (v4):sky blue (v2)
"#d985f7:#6d9eff":40,\
#purple (v4):sky blue (v3)
"#d985f7:#32a8f8":45,\
#purple (v4):sky blue (v4)
"#d985f7:#5caeff":40,\
#purple (v4):sky blue (v5)
"#d985f7:#7ba6fc":30,\
#purple (v4):blue
"#d985f7:#6292ff":40,\
#purple (v4):sky-teal-blue
"#d985f7:#28d7ff":45,\
#purple (v4):purple blue
"#d985f7:#9380ff":15,\
#purple (v4):teal-blue (v1)
"#d985f7:#3bc1f0":25,\
#purple (v4):teal-blue (v2)
"#d985f7:#34caf0":25,\
#purple (v4):teal-blue (v3)
"#d985f7:#01b0ed":55,\
#purple (v4):gold (v2)
"#d985f7:#f9cd48":40,\
#purple (v4):gold (v3)
"#d985f7:#fed940":40,\
#purple (v4):gold (v4)
"#d985f7:#ffd700":50,\
#purple (v4):orange (v2)
"#d985f7:#ffaa5f":30,\
#purple (v4):light orange
"#d985f7:#ffae7c":25,\
#purple (v4):yellow-orange
"#d985f7:#ffca5f":25,\
#purple (v4):yellow (v1)
"#d985f7:#fff03a":35,\
#purple (v4):yellow (v2)
"#d985f7:#ebdf59":35,\
#purple (v4):yellow (v3)
"#d985f7:#f1e157":35,\
#purple (v4):pink orange
"#d985f7:#ff9a84":20,\
#purple (v4):indigo (v1)
"#d985f7:#c97fff":1,\
#purple (v4):indigo (v2)
"#d985f7:#6e76ff":15,\

#purple (v5):turquoise
"#7f5fff:#01edd2":50,\
#purple (v5):medium purple
"#7f5fff:#c66aff":15,\
#purple (v5):light electric pink (v1)
"#7f5fff:#eb61ff":15,\
#purple (v5):light electric pink (v2)
"#7f5fff:#fc90ff":15,\
#purple (v5):electric pink
"#7f5fff:#f574ff":15,\
#purple (v5):dark electric pink
"#7f5fff:#ff60e1":15,\
#purple (v5):coral
"#7f5fff:#f88379":30,\
#purple (v5):purple (v1)
"#7f5fff:#977aff":7,\
#purple (v5):purple (v2)
"#7f5fff:#a971fc":7,\
#purple (v5):purple (v3)
"#7f5fff:#b76eff":10,\
#purple (v5):purple (v4)
"#7f5fff:#d985f7":15,\
#purple (v5):purple (v5)
"#7f5fff:#7f5fff":0,\
#purple (v5):purple (v6)
"#7f5fff:#a991ff":10,\
#purple (v5):purple (v7)
"#7f5fff:#a293ff":10,\
#purple (v5):pink (v2)
"#7f5fff:#ff7d9c":25,\
#purple (v5):pink (v3)
"#7f5fff:#fc98bc":15,\
#purple (v5):reddish (v1)
"#7f5fff:#ff5f5f":55,\
#purple (v5):reddish (v2)
"#7f5fff:#ff5a5a":55,\
#purple (v5):tomato
"#7f5fff:#ff8282":30,\
#purple (v5):greenish yellow
"#7f5fff:#d4d900":70,\
#purple (v5):greenish
"#7f5fff:#c8ff28":60,\
#purple (v5):aquamarine (v1)
"#7f5fff:#28ffaa":45,\
#purple (v5):aquamarine (v2)
"#7f5fff:#00eccb":30,\
#purple (v5):firozi (v2)
"#7f5fff:#2ff6ea":35,\
#purple (v5):firozi (v3)
"#7f5fff:#49d9ff":20,\
#purple (v5):firozi (v4)
"#7f5fff:#31e6ed":25,\
#purple (v5):dull green
"#7f5fff:#89e46c":40,\
#purple (v5):mint greenish
"#7f5fff:#9de245":45,\
#purple (v5):mint green
"#7f5fff:#66ff3a":75,\
#purple (v5):light mint green
"#7f5fff:#00f0a9":40,\
#purple (v5):light green
"#7f5fff:#a5ed31":50,\
#purple (v5):green (v2)
"#7f5fff:#2ff06f":55,\
#purple (v5):green (v3)
"#7f5fff:#26e99c":40,\
#purple (v5):green (v4)
"#7f5fff:#42ec72":45,\
#purple (v5):green (v5)
"#7f5fff:#46ec5c":45,\
#purple (v5):green (v6)
"#7f5fff:#50f777":40,\
#purple (v5):green (v7)
"#7f5fff:#01f5a1":30,\
#purple (v5):green (v8)
"#7f5fff:#42e966":35,\
#purple (v5):green (v9)
"#7f5fff:#52f578":30,\
#purple (v5):sky blue (v1)
"#7f5fff:#69baf5":7,\
#purple (v5):sky blue (v2)
"#7f5fff:#6d9eff":1,\
#purple (v5):sky blue (v3)
"#7f5fff:#32a8f8":5,\
#purple (v5):sky blue (v4)
"#7f5fff:#5caeff":7,\
#purple (v5):sky blue (v5)
"#7f5fff:#7ba6fc":5,\
#purple (v5):blue
"#7f5fff:#6292ff":1,\
#purple (v5):sky-teal-blue
"#7f5fff:#28d7ff":15,\
#purple (v5):purple blue
"#7f5fff:#9380ff":5,\
#purple (v5):teal-blue (v1)
"#7f5fff:#3bc1f0":15,\
#purple (v5):teal-blue (v2)
"#7f5fff:#34caf0":15,\
#purple (v5):teal-blue (v3)
"#7f5fff:#01b0ed":20,\
#purple (v5):gold (v2)
"#7f5fff:#f9cd48":50,\
#purple (v5):gold (v3)
"#7f5fff:#fed940":50,\
#purple (v5):gold (v4)
"#7f5fff:#ffd700":80,\
#purple (v5):orange (v2)
"#7f5fff:#ffaa5f":50,\
#purple (v5):light orange
"#7f5fff:#ffae7c":45,\
#purple (v5):yellow-orange
"#7f5fff:#ffca5f":40,\
#purple (v5):yellow (v1)
"#7f5fff:#fff03a":45,\
#purple (v5):yellow (v2)
"#7f5fff:#ebdf59":35,\
#purple (v5):yellow (v3)
"#7f5fff:#f1e157":35,\
#purple (v5):pink orange
"#7f5fff:#ff9a84":60,\
#purple (v5):indigo (v1)
"#7f5fff:#c97fff":15,\
#purple (v5):indigo (v2)
"#7f5fff:#6e76ff":1,\

#purple (v6):turquoise
"#a991ff:#01edd2":30,\
#purple (v6):medium purple
"#a991ff:#c66aff":5,\
#purple (v6):light electric pink (v1)
"#a991ff:#eb61ff":10,\
#purple (v6):light electric pink (v2)
"#a991ff:#fc90ff":7,\
#purple (v6):electric pink
"#a991ff:#f574ff":7,\
#purple (v6):dark electric pink
"#a991ff:#ff60e1":7,\
#purple (v6):coral
"#a991ff:#f88379":12,\
#purple (v6):purple (v1)
"#a991ff:#977aff":5,\
#purple (v6):purple (v2)
"#a991ff:#a971fc":5,\
#purple (v6):purple (v3)
"#a991ff:#b76eff":1,\
#purple (v6):purple (v4)
"#a991ff:#d985f7":10,\
#purple (v6):purple (v5)
"#a991ff:#7f5fff":10,\
#purple (v6):purple (v6)
"#a991ff:#a991ff":0,\
#purple (v6):purple (v7)
"#a991ff:#a293ff":1,\
#purple (v6):pink (v2)
"#a991ff:#ff7d9c":20,\
#purple (v6):pink (v3)
"#a991ff:#fc98bc":15,\
#purple (v6):reddish (v1)
"#a991ff:#ff5f5f":40,\
#purple (v6):reddis (v2)
"#a991ff:#ff5a5a":40,\
#purple (v6):tomato
"#a991ff:#ff8282":35,\
#purple (v6):greenish yellow
"#a991ff:#d4d900":55,\
#purple (v6):greenish
"#a991ff:#c8ff28":50,\
#purple (v6):aquamarine (v1)
"#a991ff:#28ffaa":35,\
#purple (v6):aquamarine (v2)
"#a991ff:#00eccb":35,\
#purple (v6):firozi (v2)
"#a991ff:#2ff6ea":30,\
#purple (v6):firozi (v3)
"#a991ff:#49d9ff":10,\
#purple (v6):firozi (v4)
"#a991ff:#31e6ed":15,\
#purple (v6):dull green
"#a991ff:#89e46c":25,\
#purple (v6):mint greenish
"#a991ff:#9de245":35,\
#purple (v6):mint green
"#a991ff:#66ff3a":55,\
#purple (v6):light mint green
"#a991ff:#00f0a9":30,\
#purple (v6):light green
"#a991ff:#a5ed31":40,\
#purple (v6):green (v2)
"#a991ff:#2ff06f":35,\
#purple (v6):green (v3)
"#a991ff:#26e99c":30,\
#purple (v6):green (v4)
"#a991ff:#42ec72":40,\
#purple (v6):green (v5)
"#a991ff:#46ec5c":45,\
#purple (v6):green (v6)
"#a991ff:#50f777":35,\
#purple (v6):green (v7)
"#a991ff:#01f5a1":30,\
#purple (v6):green (v8)
"#a991ff:#42e966":35,\
#purple (v6):green (v9)
"#a991ff:#52f578":25,\
#purple (v6):sky blue (v1)
"#a991ff:#69baf5":10,\
#purple (v6):sky blue (v2)
"#a991ff:#6d9eff":10,\
#purple (v6):sky blue (v3)
"#a991ff:#32a8f8":15,\
#purple (v6):sky blue (v4)
"#a991ff:#5caeff":10,\
#purple (v6):sky blue (v5)
"#a991ff:#7ba6fc":5,\
#purple (v6):blue
"#a991ff:#6292ff":7,\
#purple (v6):sky-teal-blue
"#a991ff:#28d7ff":15,\
#purple (v6):purple blue
"#a991ff:#9380ff":1,\
#purple (v6):teal-blue (v1)
"#a991ff:#3bc1f0":15,\
#purple (v6):teal-blue (v2)
"#a991ff:#34caf0":15,\
#purple (v6):teal-blue (v3)
"#a991ff:#01b0ed":10,\
#purple (v6):gold (v2)
"#a991ff:#f9cd48":45,\
#purple (v6):gold (v3)
"#a991ff:#fed940":40,\
#purple (v6):gold (v4)
"#a991ff:#ffd700":55,\
#purple (v6):orange (v2)
"#a991ff:#ffaa5f":35,\
#purple (v6):light orange
"#a991ff:#ffae7c":30,\
#purple (v6):yellow-orange
"#a991ff:#ffca5f":40,\
#purple (v6):yellow (v1)
"#a991ff:#fff03a":40,\
#purple (v6):yellow (v2)
"#a991ff:#ebdf59":30,\
#purple (v6):yellow (v3)
"#a991ff:#f1e157":30,\
#purple (v6):pink orange
"#a991ff:#ff9a84":25,\
#purple (v6):indigo (v1)
"#a991ff:#c97fff":5,\
#purple (v6):indigo (v2)
"#a991ff:#6e76ff":5,\

#purple (v7):turquoise
"#a293ff:#01edd2":30,\
#purple (v7):medium purple
"#a293ff:#c66aff":5,\
#purple (v7):light electric pink (v1)
"#a293ff:#eb61ff":10,\
#purple (v7):light electric pink (v2)
"#a293ff:#fc90ff":7,\
#purple (v7):electric pink
"#a293ff:#f574ff":7,\
#purple (v7):dark electric pink
"#a293ff:#ff60e1":7,\
#purple (v7):coral
"#a293ff:#f88379":12,\
#purple (v7):purple (v1)
"#a293ff:#977aff":3,\
#purple (v7):purple (v2)
"#a293ff:#a971fc":5,\
#purple (v7):purple (v3)
"#a293ff:#b76eff":1,\
#purple (v7):purple (v4)
"#a293ff:#d985f7":10,\
#purple (v7):purple (v5)
"#a293ff:#7f5fff":10,\
#purple (v7):purple (v6)
"#a293ff:#a991ff":1,\
#purple (v7):purple (v7)
"#a293ff:#a293ff":0,\
#purple (v7):pink (v2)
"#a293ff:#ff7d9c":20,\
#purple (v7):pink (v3)
"#a293ff:#fc98bc":15,\
#purple (v7):reddish (v1)
"#a293ff:#ff5f5f":40,\
#purple (v7):reddis (v2)
"#a293ff:#ff5a5a":40,\
#purple (v7):tomato
"#a293ff:#ff8282":30,\
#purple (v7):greenish yellow
"#a293ff:#d4d900":50,\
#purple (v7):greenish
"#a293ff:#c8ff28":40,\
#purple (v7):aquamarine (v1)
"#a293ff:#28ffaa":40,\
#purple (v7):aquamarine (v2)
"#a293ff:#00eccb":30,\
#purple (v7):firozi (v2)
"#a293ff:#2ff6ea":25,\
#purple (v7):firozi (v3)
"#a293ff:#49d9ff":20,\
#purple (v7):firozi (v4)
"#a293ff:#31e6ed":25,\
#purple (v7):dull green
"#a293ff:#89e46c":35,\
#purple (v7):mint greenish
"#a293ff:#9de245":40,\
#purple (v7):mint green
"#a293ff:#66ff3a":50,\
#purple (v7):light mint green
"#a293ff:#00f0a9":40,\
#purple (v7):light green
"#a293ff:#a5ed31":50,\
#purple (v7):green (v2)
"#a293ff:#2ff06f":35,\
#purple (v7):green (v3)
"#a293ff:#26e99c":25,\
#purple (v7):green (v4)
"#a293ff:#42ec72":30,\
#purple (v7):green (v5)
"#a293ff:#46ec5c":30,\
#purple (v7):green (v6)
"#a293ff:#50f777":25,\
#purple (v7):green (v7)
"#a293ff:#01f5a1":50,\
#purple (v7):green (v8)
"#a293ff:#42e966":40,\
#purple (v7):green (v9)
"#a293ff:#52f578":30,\
#purple (v7):sky blue (v1)
"#a293ff:#69baf5":5,\
#purple (v7):sky blue (v2)
"#a293ff:#6d9eff":5,\
#purple (v7):sky blue (v3)
"#a293ff:#32a8f8":15,\
#purple (v7):sky blue (v4)
"#a293ff:#5caeff":5,\
#purple (v7):sky blue (v5)
"#a293ff:#7ba6fc":1,\
#purple (v7):blue
"#a293ff:#6292ff":7,\
#purple (v7):sky-teal-blue
"#a293ff:#28d7ff":15,\
#purple (v7):purple blue
"#a293ff:#9380ff":1,\
#purple (v7):teal-blue (v1)
"#a293ff:#3bc1f0":15,\
#purple (v7):teal-blue (v2)
"#a293ff:#34caf0":15,\
#purple (v7):teal-blue (v3)
"#a293ff:#01b0ed":20,\
#purple (v7):gold (v2)
"#a293ff:#f9cd48":50,\
#purple (v7):gold (v3)
"#a293ff:#fed940":45,\
#purple (v7):gold (v4)
"#a293ff:#ffd700":70,\
#purple (v7):orange (v2)
"#a293ff:#ffaa5f":40,\
#purple (v7):light orange
"#a293ff:#ffae7c":40,\
#purple (v7):yellow-orange
"#a293ff:#ffca5f":45,\
#purple (v7):yellow (v1)
"#a293ff:#fff03a":35,\
#purple (v7):yellow (v2)
"#a293ff:#ebdf59":40,\
#purple (v7):yellow (v3)
"#a293ff:#f1e157":40,\
#purple (v7):pink orange
"#a293ff:#ff9a84":45,\
#purple (v7):indigo (v1)
"#a293ff:#c97fff":5,\
#purple (v7):indigo (v2)
"#a293ff:#6e76ff":5,\

#pink (v2):turquoise
"#ff7d9c:#01edd2":60,\
#pink (v2):medium purple
"#ff7d9c:#c66aff":30,\
#pink (v2):light electric pink (v1)
"#ff7d9c:#eb61ff":15,\
#pink (v2):light electric pink (v2)
"#ff7d9c:#fc90ff":10,\
#pink (v2):electric pink
"#ff7d9c:#f574ff":10,\
#pink (v2):dark electric pink
"#ff7d9c:#ff60e1":7,\
#pink (v2):coral
"#ff7d9c:#f88379":5,\
#pink (v2):purple (v1)
"#ff7d9c:#977aff":25,\
#pink (v2):purple (v2)
"#ff7d9c:#a971fc":20,\
#pink (v2):purple (v3)
"#ff7d9c:#b76eff":20,\
#pink (v2):purple (v4)
"#ff7d9c:#d985f7":15,\
#pink (v2):purple (v5)
"#ff7d9c:#7f5fff":25,\
#pink (v2):purple (v6)
"#ff7d9c:#a991ff":20,\
#pink (v2):purple (v7)
"#ff7d9c:#a293ff":20,\
#pink (v2):pink (v2)
"#ff7d9c:#ff7d9c":0,\
#pink (v2):pink (v3)
"#ff7d9c:#fc98bc":10,\
#pink (v2):reddish (v1)
"#ff7d9c:#ff5f5f":10,\
#pink (v2):reddish (v2)
"#ff7d9c:#ff5a5a":10,\
#pink (v2):tomato
"#ff7d9c:#ff8282":1,\
#pink (v2):greenish yellow
"#ff7d9c:#d4d900":35,\
#pink (v2):greenish
"#ff7d9c:#c8ff28":30,\
#pink (v2):aquamarine (v1)
"#ff7d9c:#28ffaa":40,\
#pink (v2):aquamarine (v2)
"#ff7d9c:#00eccb":40,\
#pink (v2):firozi (v2)
"#ff7d9c:#2ff6ea":35,\
#pink (v2):firozi (v3)
"#ff7d9c:#49d9ff":40,\
#pink (v2):firozi (v4)
"#ff7d9c:#31e6ed":35,\
#pink (v2):dull green
"#ff7d9c:#89e46c":45,\
#pink (v2):mint greenish
"#ff7d9c:#9de245":50,\
#pink (v2):mint green
"#ff7d9c:#66ff3a":60,\
#pink (v2):light mint green
"#ff7d9c:#00f0a9":55,\
#pink (v2):light green
"#ff7d9c:#a5ed31":45,\
#pink (v2):green (v2)
"#ff7d9c:#2ff06f":40,\
#pink (v2):green (v3)
"#ff7d9c:#26e99c":45,\
#pink (v2):green (v4)
"#ff7d9c:#42ec72":50,\
#pink (v2):green (v5)
"#ff7d9c:#46ec5c":60,\
#pink (v2):green (v6)
"#ff7d9c:#50f777":50,\
#pink (v2):green (v7)
"#ff7d9c:#01f5a1":60,\
#pink (v2):green (v8)
"#ff7d9c:#42e966":60,\
#pink (v2):green (v9)
"#ff7d9c:#52f578":50,\
#pink (v2):sky blue (v1)
"#ff7d9c:#69baf5":45,\
#pink (v2):sky blue (v2)
"#ff7d9c:#6d9eff":65,\
#pink (v2):sky blue (v3)
"#ff7d9c:#32a8f8":70,\
#pink (v2):sky blue (v4)
"#ff7d9c:#5caeff":60,\
#pink (v2):sky blue (v5)
"#ff7d9c:#7ba6fc":50,\
#pink (v2):blue
"#ff7d9c:#6292ff":65,\
#pink (v2):sky-teal-blue
"#ff7d9c:#28d7ff":40,\
#pink (v2):purple blue
"#ff7d9c:#9380ff":30,\
#pink (v2):teal-blue (v1)
"#ff7d9c:#3bc1f0":30,\
#pink (v2):teal-blue (v2)
"#ff7d9c:#34caf0":30,\
#pink (v2):teal-blue (v3)
"#ff7d9c:#01b0ed":40,\
#pink (v2):gold (v2)
"#ff7d9c:#f9cd48":30,\
#pink (v2):gold (v3)
"#ff7d9c:#fed940":30,\
#pink (v2):gold (v4)
"#ff7d9c:#ffd700":55,\
#pink (v2):orange (v2)
"#ff7d9c:#ffaa5f":15,\
#pink (v2):light orange
"#ff7d9c:#ffae7c":15,\
#pink (v2):yellow-orange
"#ff7d9c:#ffca5f":20,\
#pink (v2):yellow (v1)
"#ff7d9c:#fff03a":30,\
#pink (v2):yellow (v2)
"#ff7d9c:#ebdf59":30,\
#pink (v2):yellow (v3)
"#ff7d9c:#f1e157":30,\
#pink (v2):pink orange
"#ff7d9c:#ff9a84":5,\
#pink (v2):indigo (v1)
"#ff7d9c:#c97fff":30,\
#pink (v2):indigo (v2)
"#ff7d9c:#6e76ff":60,\

#pink (v3):turquoise
"#fc98bc:#01edd2":40,\
#pink (v3):medium purple
"#fc98bc:#c66aff":20,\
#pink (v3):light electric pink (v1)
"#fc98bc:#eb61ff":10,\
#pink (v3):light electric pink (v2)
"#fc98bc:#fc90ff":5,\
#pink (v3):electric pink
"#fc98bc:#f574ff":5,\
#pink (v3):dark electric pink
"#fc98bc:#ff60e1":5,\
#pink (v3):coral
"#fc98bc:#f88379":5,\
#pink (v3):purple (v1)
"#fc98bc:#977aff":15,\
#pink (v3):purple (v2)
"#fc98bc:#a971fc":15,\
#pink (v3):purple (v3)
"#fc98bc:#b76eff":15,\
#pink (v3):purple (v4)
"#fc98bc:#d985f7":10,\
#pink (v3):purple (v5)
"#fc98bc:#7f5fff":15,\
#pink (v3):purple (v6)
"#fc98bc:#a991ff":15,\
#pink (v3):purple (v7)
"#fc98bc:#a293ff":15,\
#pink (v3):pink (v2)
"#fc98bc:#ff7d9c":10,\
#pink (v3):pink (v3)
"#fc98bc:#fc98bc":0,\
#pink (v3):reddish (v1)
"#fc98bc:#ff5f5f":10,\
#pink (v3):reddish (v2)
"#fc98bc:#ff5a5a":10,\
#pink (v3):tomato
"#fc98bc:#ff8282":5,\
#pink (v3):greenish yellow
"#fc98bc:#d4d900":50,\
#pink (v3):greenish
"#fc98bc:#c8ff28":40,\
#pink (v3):aquamarine (v1)
"#fc98bc:#28ffaa":45,\
#pink (v3):aquamarine (v2)
"#fc98bc:#00eccb":50,\
#pink (v3):firozi (v2)
"#fc98bc:#2ff6ea":40,\
#pink (v3):firozi (v3)
"#fc98bc:#49d9ff":50,\
#pink (v3):firozi (v4)
"#fc98bc:#31e6ed":55,\
#pink (v3):dull green
"#fc98bc:#89e46c":35,\
#pink (v3):mint greenish
"#fc98bc:#9de245":40,\
#pink (v3):mint green
"#fc98bc:#66ff3a":55,\
#pink (v3):light mint green
"#fc98bc:#00f0a9":50,\
#pink (v3):light green
"#fc98bc:#a5ed31":55,\
#pink (v3):green (v32)
"#fc98bc:#2ff06f":50,\
#pink (v3):green (v3)
"#fc98bc:#26e99c":50,\
#pink (v3):green (v4)
"#fc98bc:#42ec72":55,\
#pink (v3):green (v5)
"#fc98bc:#46ec5c":55,\
#pink (v3):green (v6)
"#fc98bc:#50f777":45,\
#pink (v3):green (v7)
"#fc98bc:#01f5a1":60,\
#pink (v3):green (v8)
"#fc98bc:#42e966":60,\
#pink (v3):green (v9)
"#fc98bc:#52f578":50,\
#pink (v3):sky blue (v1)
"#fc98bc:#69baf5":50,\
#pink (v3):sky blue (v2)
"#fc98bc:#6d9eff":55,\
#pink (v3):sky blue (v3)
"#fc98bc:#32a8f8":60,\
#pink (v3):sky blue (v4)
"#fc98bc:#5caeff":50,\
#pink (v3):sky blue (v5)
"#fc98bc:#7ba6fc":45,\
#pink (v3):blue
"#fc98bc:#6292ff":55,\
#pink (v3):sky-teal-blue
"#fc98bc:#28d7ff":40,\
#pink (v3):purple blue
"#fc98bc:#9380ff":45,\
#pink (v3):teal-blue (v1)
"#fc98bc:#3bc1f0":40,\
#pink (v3):teal-blue (v2)
"#fc98bc:#34caf0":40,\
#pink (v3):teal-blue (v3)
"#fc98bc:#01b0ed":50,\
#pink (v3):gold (v2)
"#fc98bc:#f9cd48":35,\
#pink (v3):gold (v3)
"#fc98bc:#fed940":35,\
#pink (v3):gold (v4)
"#fc98bc:#ffd700":45,\
#pink (v3):orange (v2)
"#fc98bc:#ffaa5f":20,\
#pink (v3):light orange
"#fc98bc:#ffae7c":20,\
#pink (v3):yellow-orange
"#fc98bc:#ffca5f":20,\
#pink (v3):yellow (v1)
"#fc98bc:#fff03a":15,\
#pink (v3):yellow (v2)
"#fc98bc:#ebdf59":15,\
#pink (v3):yellow (v3)
"#fc98bc:#f1e157":15,\
#pink (v3):pink orange
"#fc98bc:#ff9a84":5,\
#pink (v3):indigo (v1)
"#fc98bc:#c97fff":20,\
#pink (v3):indigo (v2)
"#fc98bc:#6e76ff":50,\

#reddish (v1):turquoise
"#ff5f5f:#01edd2":75,\
#reddish (v1):medium purple
"#ff5f5f:#c66aff":50,\
#reddish (v1):light electric pink (v1)
"#ff5f5f:#eb61ff":25,\
#reddish (v1):light electric pink (v2)
"#ff5f5f:#fc90ff":20,\
#reddish (v1):electric pink
"#ff5f5f:#f574ff":17,\
#reddish (v1):dark electric pink
"#ff5f5f:#ff60e1":15,\
#reddish (v1):coral
"#ff5f5f:#f88379":5,\
#reddish (v1):purple (v1)
"#ff5f5f:#977aff":45,\
#reddish (v1):purple (v2)
"#ff5f5f:#a971fc":35,\
#reddish (v1):purple (v3)
"#ff5f5f:#b76eff":35,\
#reddish (v1):purple (v4)
"#ff5f5f:#d985f7":30,\
#reddish (v1):purple (v5)
"#ff5f5f:#7f5fff":55,\
#reddish (v1):purple (v6)
"#ff5f5f:#a991ff":40,\
#reddish (v1):purple (v7)
"#ff5f5f:#a293ff":40,\
#reddish (v1):pink (v2)
"#ff5f5f:#ff7d9c":10,\
#reddish (v1):pink (v3)
"#ff5f5f:#fc98bc":10,\
#reddish (v1):reddish (v1)
"#ff5f5f:#ff5f5f":0,\
#reddish (v1):reddish (v2)
"#ff5f5f:#ff5a5a":0,\
#reddish (v1):tomato
"#ff5f5f:#ff8282":10,\
#reddish (v1):greenish yellow
"#ff5f5f:#d4d900":40,\
#reddish (v1):greenish
"#ff5f5f:#c8ff28":40,\
#reddish (v1):aquamarine (v1)
"#ff5f5f:#28ffaa":40,\
#reddish (v1):aquamarine (v2)
"#ff5f5f:#00eccb":45,\
#reddish (v1):firozi (v2)
"#ff5f5f:#2ff6ea":40,\
#reddish (v1):firozi (v3)
"#ff5f5f:#49d9ff":40,\
#reddish (v1):firozi (v4)
"#ff5f5f:#31e6ed":45,\
#reddish (v1):dull green
"#ff5f5f:#89e46c":50,\
#reddish (v1):mint greenish
"#ff5f5f:#9de245":50,\
#reddish (v1):mint green
"#ff5f5f:#66ff3a":60,\
#reddish (v1):light mint green
"#ff5f5f:#00f0a9":45,\
#reddish (v1):light green
"#ff5f5f:#a5ed31":50,\
#reddish (v1):green (v2)
"#ff5f5f:#2ff06f":40,\
#reddish (v1):green (v3)
"#ff5f5f:#26e99c":40,\
#reddish (v1):green (v4)
"#ff5f5f:#42ec72":40,\
#reddish (v1):green (v5)
"#ff5f5f:#46ec5c":40,\
#reddish (v1):green (v6)
"#ff5f5f:#50f777":40,\
#reddish (v1):green (v7)
"#ff5f5f:#01f5a1":40,\
#reddish (v1):green (v8)
"#ff5f5f:#42e966":45,\
#reddish (v1):green (v9)
"#ff5f5f:#52f578":40,\
#reddish (v1):sky blue (v1)
"#ff5f5f:#69baf5":60,\
#reddish (v1):sky blue (v2)
"#ff5f5f:#6d9eff":65,\
#reddish (v1):sky blue (v3)
"#ff5f5f:#32a8f8":70,\
#reddish (v1):sky blue (v4)
"#ff5f5f:#5caeff":60,\
#reddish (v1):sky blue (v5)
"#ff5f5f:#7ba6fc":50,\
#reddish (v1):blue
"#ff5f5f:#6292ff":70,\
#reddish (v1):sky-teal-blue
"#ff5f5f:#28d7ff":70,\
#reddish (v1):purple blue
"#ff5f5f:#9380ff":35,\
#reddish (v1):teal-blue (v1)
"#ff5f5f:#3bc1f0":30,\
#reddish (v1):teal-blue (v2)
"#ff5f5f:#34caf0":30,\
#reddish (v1):teal-blue (v3)
"#ff5f5f:#01b0ed":40,\
#reddish (v1):gold (v2)
"#ff5f5f:#f9cd48":35,\
#reddish (v1):gold (v3)
"#ff5f5f:#fed940":35,\
#reddish (v1):gold (v4)
"#ff5f5f:#ffd700":55,\
#reddish (v1):orange (v2)
"#ff5f5f:#ffaa5f":10,\
#reddish (v1):light orange
"#ff5f5f:#ffae7c":15,\
#reddish (v1):yellow-orange
"#ff5f5f:#ffca5f":15,\
#reddish (v1):yellow (v1)
"#ff5f5f:#fff03a":25,\
#reddish (v1):yellow (v2)
"#ff5f5f:#ebdf59":30,\
#reddish (v1):yellow (v3)
"#ff5f5f:#f1e157":30,\
#reddish (v1):pink orange
"#ff5f5f:#ff9a84":5,\
#reddish (v1):indigo (v1)
"#ff5f5f:#c97fff":35,\
#reddish (v1):indigo (v2)
"#ff5f5f:#6e76ff":45,\

#reddish (v2):turquoise
"#ff5a5a:#01edd2":80,\
#reddish (v2):medium purple
"#ff5a5a:#c66aff":50,\
#reddish (v2):light electric pink (v1)
"#ff5a5a:#eb61ff":25,\
#reddish (v2):light electric pink (v2)
"#ff5a5a:#fc90ff":20,\
#reddish (v2):electric pink
"#ff5a5a:#f574ff":18,\
#reddish (v2):dark electric pink
"#ff5a5a:#ff60e1":15,\
#reddish (v2):coral
"#ff5a5a:#f88379":5,\
#reddish (v2):purple (v1)
"#ff5a5a:#977aff":45,\
#reddish (v2):purple (v2)
"#ff5a5a:#a971fc":35,\
#reddish (v2):purple (v3)
"#ff5a5a:#b76eff":35,\
#reddish (v2):purple (v4)
"#ff5a5a:#d985f7":30,\
#reddish (v2):purple (v5)
"#ff5a5a:#7f5fff":55,\
#reddish (v2):purple (v6)
"#ff5a5a:#a991ff":40,\
#reddish (v2):purple (v7)
"#ff5a5a:#a293ff":40,\
#reddish (v2):pink (v2)
"#ff5a5a:#ff7d9c":10,\
#reddish (v2):pink (v3)
"#ff5a5a:#fc98bc":10,\
#reddish (v2):reddish (v1)
"#ff5a5a:#ff5f5f":0,\
#reddish (v2):reddish (v2)
"#ff5a5a:#ff5a5a":0,\
#reddish (v2):tomato
"#ff5a5a:#ff8282":5,\
#reddish (v2):greenish yellow
"#ff5a5a:#d4d900":45,\
#reddish (v2):greenish
"#ff5a5a:#c8ff28":40,\
#reddish (v2):aquamarine (v1)
"#ff5a5a:#28ffaa":45,\
#reddish (v2):aquamarine (v2)
"#ff5a5a:#00eccb":55,\
#reddish (v2):firozi (v2)
"#ff5a5a:#2ff6ea":45,\
#reddish (v2):firozi (v3)
"#ff5a5a:#49d9ff":45,\
#reddish (v2):firozi (v4)
"#ff5a5a:#31e6ed":50,\
#reddish (v2):dull green
"#ff5a5a:#89e46c":35,\
#reddish (v2):mint greenish
"#ff5a5a:#9de245":40,\
#reddish (v2):mint green
"#ff5a5a:#66ff3a":50,\
#reddish (v2):light mint green
"#ff5a5a:#00f0a9":45,\
#reddish (v2):light green
"#ff5a5a:#a5ed31":40,\
#reddish (v2):green (v2)
"#ff5a5a:#2ff06f":40,\
#reddish (v2):green (v3)
"#ff5a5a:#26e99c":40,\
#reddish (v2):green (v4)
"#ff5a5a:#42ec72":45,\
#reddish (v2):green (v5)
"#ff5a5a:#46ec5c":45,\
#reddish (v2):green (v6)
"#ff5a5a:#50f777":40,\
#reddish (v2):green (v7)
"#ff5a5a:#01f5a1":50,\
#reddish (v2):green (v8)
"#ff5a5a:#42e966":50,\
#reddish (v2):green (v9)
"#ff5a5a:#52f578":45,\
#reddish (v2):sky blue (v1)
"#ff5a5a:#69baf5":50,\
#reddish (v2):sky blue (v2)
"#ff5a5a:#6d9eff":55,\
#reddish (v2):sky blue (v3)
"#ff5a5a:#32a8f8":60,\
#reddish (v2):sky blue (v4)
"#ff5a5a:#5caeff":55,\
#reddish (v2):sky blue (v5)
"#ff5a5a:#7ba6fc":50,\
#reddish (v2):blue
"#ff5a5a:#6292ff":60,\
#reddish (v2):sky-teal-blue
"#ff5a5a:#28d7ff":45,\
#reddish (v2):purple blue
"#ff5a5a:#9380ff":40,\
#reddish (v2):teal-blue (v1)
"#ff5a5a:#3bc1f0":40,\
#reddish (v2):teal-blue (v2)
"#ff5a5a:#34caf0":40,\
#reddish (v2):teal-blue (v3)
"#ff5a5a:#01b0ed":50,\
#reddish (v2):gold (v2)
"#ff5a5a:#f9cd48":30,\
#reddish (v2):gold (v3)
"#ff5a5a:#fed940":30,\
#reddish (v2):gold (v4)
"#ff5a5a:#ffd700":40,\
#reddish (v2):orange (v2)
"#ff5a5a:#ffaa5f":10,\
#reddish (v2):light orange
"#ff5a5a:#ffae7c":15,\
#reddish (v2):yellow-orange
"#ff5a5a:#ffca5f":20,\
#reddish (v2):yellow (v1)
"#ff5a5a:#fff03a":25,\
#reddish (v2):yellow (v2)
"#ff5a5a:#ebdf59":30,\
#reddish (v2):yellow (v3)
"#ff5a5a:#f1e157":30,\
#reddish (v2):pink orange
"#ff5a5a:#ff9a84":7,\
#reddish (v2):indigo (v1)
"#ff5a5a:#c97fff":30,\
#reddish (v2):indigo (v2)
"#ff5a5a:#6e76ff":60,\

#tomato:turquoise
"#ff8282:#01edd2":55,\
#tomato:medium purple
"#ff8282:#c66aff":30,\
#tomato:light electric pink (v1)
"#ff8282:#eb61ff":15,\
#tomato:light electric pink (v2)
"#ff8282:#fc90ff":10,\
#tomato:electric pink
"#ff8282:#f574ff":10,\
#tomato:dark electric pink
"#ff8282:#ff60e1":10,\
#tomato:coral
"#ff8282:#f88379":1,\
#tomato:purple (v1)
"#ff8282:#977aff":20,\
#tomato:purple (v2)
"#ff8282:#a971fc":20,\
#tomato:purple (v3)
"#ff8282:#b76eff":15,\
#tomato:purple (v4)
"#ff8282:#d985f7":20,\
#tomato:purple (v5)
"#ff8282:#7f5fff":30,\
#tomato:purple (v6)
"#ff8282:#a991ff":35,\
#tomato:purple (v7)
"#ff8282:#a293ff":30,\
#tomato:pink (v2)
"#ff8282:#ff7d9c":1,\
#tomato:pink (v3)
"#ff8282:#fc98bc":5,\
#tomato:reddish (v1)
"#ff8282:#ff5f5f":10,\
#tomato:reddish (v2)
"#ff8282:#ff5a5a":5,\
#tomato:tomato
"#ff8282:#ff8282":0,\
#tomato:greenish yellow
"#ff8282:#d4d900":35,\
#tomato:greenish
"#ff8282:#c8ff28":30,\
#tomato:aquamarine (v1)
"#ff8282:#28ffaa":35,\
#tomato:aquamarine (v2)
"#ff8282:#00eccb":45,\
#tomato:firozi (v2)
"#ff8282:#2ff6ea":40,\
#tomato:firozi (v3)
"#ff8282:#49d9ff":40,\
#tomato:firozi (v4)
"#ff8282:#31e6ed":45,\
#tomato:dull green
"#ff8282:#89e46c":35,\
#tomato:mint greenish
"#ff8282:#9de245":35,\
#tomato:mint green
"#ff8282:#66ff3a":55,\
#tomato:light mint green
"#ff8282:#00f0a9":45,\
#tomato:light green
"#ff8282:#a5ed31":30,\
#tomato:green (v2)
"#ff8282:#2ff06f":40,\
#tomato:green (v3)
"#ff8282:#26e99c":40,\
#tomato:green (v4)
"#ff8282:#42ec72":45,\
#tomato:green (v5)
"#ff8282:#46ec5c":45,\
#tomato:green (v6)
"#ff8282:#50f777":40,\
#tomato:green (v7)
"#ff8282:#01f5a1":50,\
#tomato:green (v8)
"#ff8282:#42e966":45,\
#tomato:green (v9)
"#ff8282:#52f578":40,\
#tomato:sky blue (v1)
"#ff8282:#69baf5":50,\
#tomato:sky blue (v2)
"#ff8282:#6d9eff":55,\
#tomato:sky blue (v3)
"#ff8282:#32a8f8":60,\
#tomato:sky blue (v4)
"#ff8282:#5caeff":50,\
#tomato:sky blue (v5)
"#ff8282:#7ba6fc":40,\
#tomato:blue
"#ff8282:#6292ff":70,\
#tomato:sky-teal-blue
"#ff8282:#28d7ff":45,\
#tomato:purple blue
"#ff8282:#9380ff":40,\
#tomato:teal-blue (v1)
"#ff8282:#3bc1f0":40,\
#tomato:teal-blue (v2)
"#ff8282:#34caf0":40,\
#tomato:teal-blue (v3)
"#ff8282:#01b0ed":50,\
#tomato:gold (v2)
"#ff8282:#f9cd48":25,\
#tomato:gold (v3)
"#ff8282:#fed940":20,\
#tomato:gold (v4)
"#ff8282:#ffd700":35,\
#tomato:orange (v2)
"#ff8282:#ffaa5f":15,\
#tomato:light orange
"#ff8282:#ffae7c":10,\
#tomato:yellow-orange
"#ff8282:#ffca5f":15,\
#tomato:yellow (v1)
"#ff8282:#fff03a":20,\
#tomato:yellow (v2)
"#ff8282:#ebdf59":25,\
#tomato:yellow (v3)
"#ff8282:#f1e157":25,\
#tomato:pink orange
"#ff8282:#ff9a84":1,\
#tomato:indigo (v1)
"#ff8282:#c97fff":40,\
#tomato:indigo (v2)
"#ff8282:#6e76ff":65,\

#greenish yellow:turquoise
"#d4d900:#01edd2":65,\
#greenish yellow:medium purple
"#d4d900:#c66aff":65,\
#greenish yellow:light electric pink (v1)
"#d4d900:#eb61ff":60,\
#greenish yellow:light electric pink (v2)
"#d4d900:#fc90ff":70,\
#greenish yellow:electric pink
"#d4d900:#f574ff":65,\
#greenish yellow:dark electric pink
"#d4d900:#ff60e1":50,\
#greenish yellow:coral
"#d4d900:#f88379":25,\
#greenish yellow:purple (v1)
"#d4d900:#977aff":65,\
#greenish yellow:purple (v2)
"#d4d900:#a971fc":55,\
#greenish yellow:purple (v3)
"#d4d900:#b76eff":60,\
#greenish yellow:purple (v4)
"#d4d900:#d985f7":45,\
#greenish yellow:purple (v5)
"#d4d900:#7f5fff":70,\
#greenish yellow:purple (v6)
"#d4d900:#a991ff":55,\
#greenish yellow:purple (v7)
"#d4d900:#a293ff":50,\
#greenish yellow:pink (v2)
"#d4d900:#ff7d9c":35,\
#greenish yellow:pink (v3)
"#d4d900:#fc98bc":50,\
#greenish yellow:reddish (v1)
"#d4d900:#ff5f5f":40,\
#greenish yellow:reddish (v2)
"#d4d900:#ff5a5a":45,\
#greenish yellow:tomato
"#d4d900:#ff8282":35,\
#greenish yellow:greenish yellow
"#d4d900:#d4d900":0,\
#greenish yellow:greenish
"#d4d900:#c8ff28":7,\
#greenish yellow:aquamarine (v1)
"#d4d900:#28ffaa":20,\
#greenish yellow:aquamarine (v2)
"#d4d900:#00eccb":30,\
#greenish yellow:firozi (v2)
"#d4d900:#2ff6ea":35,\
#greenish yellow:firozi (v3)
"#d4d900:#49d9ff":45,\
#greenish yellow:firozi (v4)
"#d4d900:#31e6ed":40,\
#greenish yellow:dull green
"#d4d900:#89e46c":15,\
#greenish yellow:mint greenish
"#d4d900:#9de245":10,\
#greenish yellow:mint green
"#d4d900:#66ff3a":15,\
#greenish yellow:light mint green
"#d4d900:#00f0a9":30,\
#greenish yellow:light green
"#d4d900:#a5ed31":7,\
#greenish yellow:green (v2)
"#d4d900:#2ff06f":25,\
#greenish yellow:green (v3)
"#d4d900:#26e99c":20,\
#greenish yellow:green (v4)
"#d4d900:#42ec72":20,\
#greenish yellow:green (v5)
"#d4d900:#46ec5c":15,\
#greenish yellow:green (v6)
"#d4d900:#50f777":20,\
#greenish yellow:green (v7)
"#d4d900:#01f5a1":30,\
#greenish yellow:green (v8)
"#d4d900:#42e966":20,\
#greenish yellow:green (v9)
"#d4d900:#52f578":15,\
#greenish yellow:sky blue (v1)
"#d4d900:#69baf5":40,\
#greenish yellow:sky blue (v2)
"#d4d900:#6d9eff":45,\
#greenish yellow:sky blue (v3)
"#d4d900:#32a8f8":55,\
#greenish yellow:sky blue (v4)
"#d4d900:#5caeff":45,\
#greenish yellow:sky blue (v5)
"#d4d900:#7ba6fc":45,\
#greenish yellow:blue
"#d4d900:#6292ff":55,\
#greenish yellow:sky-teal-blue
"#d4d900:#28d7ff":40,\
#greenish yellow:purple blue
"#d4d900:#9380ff":60,\
#greenish yellow:teal-blue (v1)
"#d4d900:#3bc1f0":45,\
#greenish yellow:teal-blue (v2)
"#d4d900:#34caf0":45,\
#greenish yellow:teal-blue (v3)
"#d4d900:#01b0ed":55,\
#greenish yellow:gold (v2)
"#d4d900:#f9cd48":10,\
#greenish yellow:gold (v3)
"#d4d900:#fed940":7,\
#greenish yellow:gold (v4)
"#d4d900:#ffd700":10,\
#greenish yellow:orange (v2)
"#d4d900:#ffaa5f":15,\
#greenish yellow:light orange
"#d4d900:#ffae7c":15,\
#greenish yellow:yellow-orange
"#d4d900:#ffca5f":10,\
#greenish yellow:yellow (v1)
"#d4d900:#fff03a":1,\
#greenish yellow:yellow (v2)
"#d4d900:#ebdf59":1,\
#greenish yellow:yellow (v3)
"#d4d900:#f1e157":1,\
#greenish yellow:pink orange
"#d4d900:#ff9a84":20,\
#greenish yellow:indigo (v1)
"#d4d900:#c97fff":40,\
#greenish yellow:indigo (v2)
"#d4d900:#6e76ff":80,\

#greenish:turquoise
"#c8ff28:#01edd2":35,\
#greenish:medium purple
"#c8ff28:#c66aff":60,\
#greenish:light electric pink (v1)
"#c8ff28:#eb61ff":50,\
#greenish:light electric pink (v2)
"#c8ff28:#fc90ff":40,\
#greenish:electric pink
"#c8ff28:#f574ff":55,\
#greenish:dark electric pink
"#c8ff28:#ff60e1":55,\
#greenish:coral
"#c8ff28:#f88379":20,\
#greenish:purple (v1)
"#c8ff28:#977aff":50,\
#greenish:purple (v2)
"#c8ff28:#a971fc":45,\
#greenish:purple (v3)
"#c8ff28:#b76eff":40,\
#greenish:purple (v4)
"#c8ff28:#d985f7":25,\
#greenish:purple (v5)
"#c8ff28:#7f5fff":60,\
#greenish:purple (v6)
"#c8ff28:#a991ff":50,\
#greenish:purple (v7)
"#c8ff28:#a293ff":40,\
#greenish:pink (v2)
"#c8ff28:#ff7d9c":30,\
#greenish:pink (v3)
"#c8ff28:#fc98bc":40,\
#greenish:reddish (v1)
"#c8ff28:#ff5f5f":40,\
#greenish:reddish (v2)
"#c8ff28:#ff5a5a":40,\
#greenish:tomato
"#c8ff28:#ff8282":30,\
#greenish:greenish yellow
"#c8ff28:#d4d900":7,\
#greenish:greenish
"#c8ff28:#c8ff28":0,\
#greenish:aquamarine (v1)
"#c8ff28:#28ffaa":15,\
#greenish:aquamarine (v2)
"#c8ff28:#00eccb":20,\
#greenish:firozi (v2)
"#c8ff28:#2ff6ea":20,\
#greenish:firozi (v3)
"#c8ff28:#49d9ff":30,\
#greenish:firozi (v4)
"#c8ff28:#31e6ed":25,\
#greenish:dull green
"#c8ff28:#89e46c":15,\
#greenish:mint greenish
"#c8ff28:#9de245":7,\
#greenish:mint green
"#c8ff28:#66ff3a":7,\
#greenish:light mint green
"#c8ff28:#00f0a9":20,\
#greenish:light green
"#c8ff28:#a5ed31":1,\
#greenish:green (v2)
"#c8ff28:#2ff06f":15,\
#greenish:green (v3)
"#c8ff28:#26e99c":15,\
#greenish:green (v4)
"#c8ff28:#42ec72":15,\
#greenish:green (v5)
"#c8ff28:#46ec5c":10,\
#greenish:green (v6)
"#c8ff28:#50f777":15,\
#greenish:green (v7)
"#c8ff28:#01f5a1":20,\
#greenish:green (v8)
"#c8ff28:#42e966":15,\
#greenish:green (v9)
"#c8ff28:#52f578":10,\
#greenish:sky blue (v1)
"#c8ff28:#69baf5":35,\
#greenish:sky blue (v2)
"#c8ff28:#6d9eff":40,\
#greenish:sky blue (v3)
"#c8ff28:#32a8f8":50,\
#greenish:sky blue (v4)
"#c8ff28:#5caeff":35,\
#greenish:sky blue (v5)
"#c8ff28:#7ba6fc":35,\
#greenish:blue
"#c8ff28:#6292ff":65,\
#greenish:sky-teal-blue
"#c8ff28:#28d7ff":35,\
#greenish:purple blue
"#c8ff28:#9380ff":45,\
#greenish:teal-blue (v1)
"#c8ff28:#3bc1f0":35,\
#greenish:teal-blue (v2)
"#c8ff28:#34caf0":35,\
#greenish:teal-blue (v3)
"#c8ff28:#01b0ed":55,\
#greenish:gold (v2)
"#c8ff28:#f9cd48":10,\
#greenish:gold (v3)
"#c8ff28:#fed940":10,\
#greenish:gold (v4)
"#c8ff28:#ffd700":15,\
#greenish:orange (v2)
"#c8ff28:#ffaa5f":20,\
#greenish:light orange
"#c8ff28:#ffae7c":20,\
#greenish:yellow-orange
"#c8ff28:#ffca5f":15,\
#greenish:yellow (v1)
"#c8ff28:#fff03a":5,\
#greenish:yellow (v2)
"#c8ff28:#ebdf59":5,\
#greenish:yellow (v3)
"#c8ff28:#f1e157":5,\
#greenish:pink orange
"#c8ff28:#ff9a84":30,\
#greenish:indigo (v1)
"#c8ff28:#c97fff":45,\
#greenish:indigo (v2)
"#c8ff28:#6e76ff":70,\

#aquamarine (v1):turquoise
"#28ffaa:#01edd2":10,\
#aquamarine (v1):medium purple
"#28ffaa:#c66aff":70,\
#aquamarine (v1):light electric pink (v1)
"#28ffaa:#eb61ff":60,\
#aquamarine (v1):light electric pink (v2)
"#28ffaa:#fc90ff":30,\
#aquamarine (v1):electric pink
"#28ffaa:#f574ff":60,\
#aquamarine (v1):dark electric pink
"#28ffaa:#ff60e1":45,\
#aquamarine (v1):coral
"#28ffaa:#f88379":40,\
#aquamarine (v1):purple (v1)
"#28ffaa:#977aff":40,\
#aquamarine (v1):purple (v2)
"#28ffaa:#a971fc":30,\
#aquamarine (v1):purple (v3)
"#28ffaa:#b76eff":30,\
#aquamarine (v1):purple (v4)
"#28ffaa:#d985f7":35,\
#aquamarine (v1):purple (v5)
"#28ffaa:#7f5fff":45,\
#aquamarine (v1):purple (v6)
"#28ffaa:#a991ff":35,\
#aquamarine (v1):purple (v7)
"#28ffaa:#a293ff":40,\
#aquamarine (v1):pink (v2)
"#28ffaa:#ff7d9c":40,\
#aquamarine (v1):pink (v3)
"#28ffaa:#fc98bc":45,\
#aquamarine (v1):reddish (v1)
"#28ffaa:#ff5f5f":40,\
#aquamarine (v1):reddish (v2)
"#28ffaa:#ff5a5a":45,\
#aquamarine (v1):tomato
"#28ffaa:#ff8282":35,\
#aquamarine (v1):greenish yellow
"#28ffaa:#d4d900":20,\
#aquamarine (v1):greenish
"#28ffaa:#c8ff28":15,\
#aquamarine (v1):aquamarine (v1)
"#28ffaa:#28ffaa":0,\
#aquamarine (v1):aquamarine (v2)
"#28ffaa:#00eccb":7,\
#aquamarine (v1):firozi (v2)
"#28ffaa:#2ff6ea":5,\
#aquamarine (v1):firozi (v3)
"#28ffaa:#49d9ff":15,\
#aquamarine (v1):firozi (v4)
"#28ffaa:#31e6ed":10,\
#aquamarine (v1):dull green
"#28ffaa:#89e46c":7,\
#aquamarine (v1):mint greenish
"#28ffaa:#9de245":10,\
#aquamarine (v1):mint green
"#28ffaa:#66ff3a":15,\
#aquamarine (v1):light mint green
"#28ffaa:#00f0a9":1,\
#aquamarine (v1):light green
"#28ffaa:#a5ed31":15,\
#aquamarine (v1):green (v2)
"#28ffaa:#2ff06f":5,\
#aquamarine (v1):green (v3)
"#28ffaa:#26e99c":1,\
#aquamarine (v1):green (v4)
"#28ffaa:#42ec72":5,\
#aquamarine (v1):green (v5)
"#28ffaa:#46ec5c":7,\
#aquamarine (v1):green (v6)
"#28ffaa:#50f777":5,\
#aquamarine (v1):green (v7)
"#28ffaa:#01f5a1":1,\
#aquamarine (v1):green (v8)
"#28ffaa:#42e966":7,\
#aquamarine (v1):green (v9)
"#28ffaa:#52f578":5,\
#aquamarine (v1):sky blue (v1)
"#28ffaa:#69baf5":25,\
#aquamarine (v1):sky blue (v2)
"#28ffaa:#6d9eff":35,\
#aquamarine (v1):sky blue (v3)
"#28ffaa:#32a8f8":40,\
#aquamarine (v1):sky blue (v4)
"#28ffaa:#5caeff":35,\
#aquamarine (v1):sky blue (v5)
"#28ffaa:#7ba6fc":35,\
#aquamarine (v1):blue
"#28ffaa:#6292ff":40,\
#aquamarine (v1):sky-teal-blue
"#28ffaa:#28d7ff":20,\
#aquamarine (v1):purple blue
"#28ffaa:#9380ff":30,\
#aquamarine (v1):teal-blue (v1)
"#28ffaa:#3bc1f0":20,\
#aquamarine (v1):teal-blue (v2)
"#28ffaa:#34caf0":20,\
#aquamarine (v1):teal-blue (v3)
"#28ffaa:#01b0ed":30,\
#aquamarine (v1):gold (v2)
"#28ffaa:#f9cd48":30,\
#aquamarine (v1):gold (v3)
"#28ffaa:#fed940":30,\
#aquamarine (v1):gold (v4)
"#28ffaa:#ffd700":45,\
#aquamarine (v1):orange (v2)
"#28ffaa:#ffaa5f":40,\
#aquamarine (v1):light orange
"#28ffaa:#ffae7c":40,\
#aquamarine (v1):yellow-orange
"#28ffaa:#ffca5f":35,\
#aquamarine (v1):yellow (v1)
"#28ffaa:#fff03a":20,\
#aquamarine (v1):yellow (v2)
"#28ffaa:#ebdf59":15,\
#aquamarine (v1):yellow (v3)
"#28ffaa:#f1e157":15,\
#aquamarine (v1):pink orange
"#28ffaa:#ff9a84":40,\
#aquamarine (v1):indigo (v1)
"#28ffaa:#c97fff":45,\
#aquamarine (v1):indigo (v2)
"#28ffaa:#6e76ff":60,\

#aquamarine (v2):turquoise
"#00eccb:#01edd2":1,\
#aquamarine (v2):medium purple
"#00eccb:#c66aff":75,\
#aquamarine (v2):light electric pink (v1)
"#00eccb:#eb61ff":40,\
#aquamarine (v2):light electric pink (v2)
"#00eccb:#fc90ff":45,\
#aquamarine (v2):electric pink
"#00eccb:#f574ff":70,\
#aquamarine (v2):dark electric pink
"#00eccb:#ff60e1":40,\
#aquamarine (v2):coral
"#00eccb:#f88379":45,\
#aquamarine (v2):purple (v1)
"#00eccb:#977aff":35,\
#aquamarine (v2):purple (v2)
"#00eccb:#a971fc":25,\
#aquamarine (v2):purple (v3)
"#00eccb:#b76eff":35,\
#aquamarine (v2):purple (v4)
"#00eccb:#d985f7":45,\
#aquamarine (v2):purple (v5)
"#00eccb:#7f5fff":30,\
#aquamarine (v2):purple (v6)
"#00eccb:#a991ff":35,\
#aquamarine (v2):purple (v7)
"#00eccb:#a293ff":30,\
#aquamarine (v2):pink (v2)
"#00eccb:#ff7d9c":40,\
#aquamarine (v2):pink (v3)
"#00eccb:#fc98bc":50,\
#aquamarine (v2):reddish (v1)
"#00eccb:#ff5f5f":45,\
#aquamarine (v2):reddish (v2)
"#00eccb:#ff5a5a":55,\
#aquamarine (v2):tomato
"#00eccb:#ff8282":45,\
#aquamarine (v2):greenish yellow
"#00eccb:#d4d900":30,\
#aquamarine (v2):greenish
"#00eccb:#c8ff28":20,\
#aquamarine (v2):aquamarine (v1)
"#00eccb:#28ffaa":7,\
#aquamarine (v2):aquamarine (v2)
"#00eccb:#00eccb":0,\
#aquamarine (v2):firozi (v2)
"#00eccb:#2ff6ea":10,\
#aquamarine (v2):firozi (v3)
"#00eccb:#49d9ff":15,\
#aquamarine (v2):firozi (v4)
"#00eccb:#31e6ed":10,\
#aquamarine (v2):dull green
"#00eccb:#89e46c":15,\
#aquamarine (v2):mint greenish
"#00eccb:#9de245":15,\
#aquamarine (v2):mint green
"#00eccb:#66ff3a":15,\
#aquamarine (v2):light mint green
"#00eccb:#00f0a9":5,\
#aquamarine (v2):light green
"#00eccb:#a5ed31":15,\
#aquamarine (v2):green (v2)
"#00eccb:#2ff06f":5,\
#aquamarine (v2):green (v3)
"#00eccb:#26e99c":1,\
#aquamarine (v2):green (v4)
"#00eccb:#42ec72":10,\
#aquamarine (v2):green (v5)
"#00eccb:#46ec5c":10,\
#aquamarine (v2):green (v6)
"#00eccb:#50f777":7,\
#aquamarine (v2):green (v7)
"#00eccb:#01f5a1":5,\
#aquamarine (v2):green (v8)
"#00eccb:#42e966":10,\
#aquamarine (v2):green (v9)
"#00eccb:#52f578":7,\
#aquamarine (v2):sky blue (v1)
"#00eccb:#69baf5":20,\
#aquamarine (v2):sky blue (v2)
"#00eccb:#6d9eff":30,\
#aquamarine (v2):sky blue (v3)
"#00eccb:#32a8f8":30,\
#aquamarine (v2):sky blue (v4)
"#00eccb:#5caeff":25,\
#aquamarine (v2):sky blue (v5)
"#00eccb:#7ba6fc":25,\
#aquamarine (v2):blue
"#00eccb:#6292ff":40,\
#aquamarine (v2):sky-teal-blue
"#00eccb:#28d7ff":10,\
#aquamarine (v2):purple blue
"#00eccb:#9380ff":45,\
#aquamarine (v2):teal-blue (v1)
"#00eccb:#3bc1f0":10,\
#aquamarine (v2):teal-blue (v2)
"#00eccb:#34caf0":10,\
#aquamarine (v2):teal-blue (v3)
"#00eccb:#01b0ed":15,\
#aquamarine (v2):gold (v2)
"#00eccb:#f9cd48":40,\
#aquamarine (v2):gold (v3)
"#00eccb:#fed940":40,\
#aquamarine (v2):gold (v4)
"#00eccb:#ffd700":55,\
#aquamarine (v2):orange (v2)
"#00eccb:#ffaa5f":35,\
#aquamarine (v2):light orange
"#00eccb:#ffae7c":30,\
#aquamarine (v2):yellow-orange
"#00eccb:#ffca5f":30,\
#aquamarine (v2):yellow (v1)
"#00eccb:#fff03a":25,\
#aquamarine (v2):yellow (v2)
"#00eccb:#ebdf59":25,\
#aquamarine (v2):yellow (v3)
"#00eccb:#f1e157":25,\
#aquamarine (v2):pink orange
"#00eccb:#ff9a84":30,\
#aquamarine (v2):indigo (v1)
"#00eccb:#c97fff":45,\
#aquamarine (v2):indigo (v2)
"#00eccb:#6e76ff":55,\

#firozi (v2):turquoise
"#2ff6ea:#01edd2":5,\
#firozi (v2):medium purple
"#2ff6ea:#c66aff":70,\
#firozi (v2):light electric pink (v1)
"#2ff6ea:#eb61ff":45,\
#firozi (v2):light electric pink (v2)
"#2ff6ea:#fc90ff":30,\
#firozi (v2):electric pink
"#2ff6ea:#f574ff":55,\
#firozi (v2):dark electric pink
"#2ff6ea:#ff60e1":35,\
#firozi (v2):coral
"#2ff6ea:#f88379":35,\
#firozi (v2):purple (v1)
"#2ff6ea:#977aff":30,\
#firozi (v2):purple (v2)
"#2ff6ea:#a971fc":30,\
#firozi (v2):purple (v3)
"#2ff6ea:#b76eff":25,\
#firozi (v2):purple (v4)
"#2ff6ea:#d985f7":35,\
#firozi (v2):purple (v5)
"#2ff6ea:#7f5fff":35,\
#firozi (v2):purple (v6)
"#2ff6ea:#a991ff":30,\
#firozi (v2):purple (v7)
"#2ff6ea:#a293ff":25,\
#firozi (v2):pink (v2)
"#2ff6ea:#ff7d9c":35,\
#firozi (v2):pink (v3)
"#2ff6ea:#fc98bc":40,\
#firozi (v2):reddish (v1)
"#2ff6ea:#ff5f5f":40,\
#firozi (v2):reddish (v2)
"#2ff6ea:#ff5a5a":45,\
#firozi (v2):tomato
"#2ff6ea:#ff8282":40,\
#firozi (v2):greenish yellow
"#2ff6ea:#d4d900":35,\
#firozi (v2):greenish
"#2ff6ea:#c8ff28":20,\
#firozi (v2):aquamarine (v1)
"#2ff6ea:#28ffaa":5,\
#firozi (v2):aquamarine (v2)
"#2ff6ea:#00eccb":10,\
#firozi (v2):firozi (v2)
"#2ff6ea:#2ff6ea":0,\
#firozi (v2):firozi (v3)
"#2ff6ea:#49d9ff":7,\
#firozi (v2):firozi (v4)
"#2ff6ea:#31e6ed":1,\
#firozi (v2):dull green
"#2ff6ea:#89e46c":15,\
#firozi (v2):mint greenish
"#2ff6ea:#9de245":20,\
#firozi (v2):mint green
"#2ff6ea:#66ff3a":25,\
#firozi (v2):light mint green
"#2ff6ea:#00f0a9":5,\
#firozi (v2):light green
"#2ff6ea:#a5ed31":20,\
#firozi (v2):green (v2)
"#2ff6ea:#2ff06f":15,\
#firozi (v2):green (v3)
"#2ff6ea:#26e99c":5,\
#firozi (v2):green (v4)
"#2ff6ea:#42ec72":10,\
#firozi (v2):green (v5)
"#2ff6ea:#46ec5c":10,\
#firozi (v2):green (v6)
"#2ff6ea:#50f777":7,\
#firozi (v2):green (v7)
"#2ff6ea:#01f5a1":5,\
#firozi (v2):green (v8)
"#2ff6ea:#42e966":15,\
#firozi (v2):green (v9)
"#2ff6ea:#52f578":10,\
#firozi (v2):sky blue (v1)
"#2ff6ea:#69baf5":15,\
#firozi (v2):sky blue (v2)
"#2ff6ea:#6d9eff":20,\
#firozi (v2):sky blue (v3)
"#2ff6ea:#32a8f8":20,\
#firozi (v2):sky blue (v4)
"#2ff6ea:#5caeff":15,\
#firozi (v2):sky blue (v5)
"#2ff6ea:#7ba6fc":15,\
#firozi (v2):blue
"#2ff6ea:#6292ff":30,\
#firozi (v2):sky-teal-blue
"#2ff6ea:#28d7ff":5,\
#firozi (v2):purple blue
"#2ff6ea:#9380ff":40,\
#firozi (v2):teal-blue (v1)
"#2ff6ea:#3bc1f0":5,\
#firozi (v2):teal-blue (v2)
"#2ff6ea:#34caf0":5,\
#firozi (v2):teal-blue (v3)
"#2ff6ea:#01b0ed":20,\
#firozi (v2):gold (v2)
"#2ff6ea:#f9cd48":45,\
#firozi (v2):gold (v3)
"#2ff6ea:#fed940":45,\
#firozi (v2):gold (v4)
"#2ff6ea:#ffd700":50,\
#firozi (v2):orange (v2)
"#2ff6ea:#ffaa5f":35,\
#firozi (v2):light orange
"#2ff6ea:#ffae7c":30,\
#firozi (v2):yellow-orange
"#2ff6ea:#ffca5f":25,\
#firozi (v2):yellow (v1)
"#2ff6ea:#fff03a":25,\
#firozi (v2):yellow (v2)
"#2ff6ea:#ebdf59":20,\
#firozi (v2):yellow (v3)
"#2ff6ea:#f1e157":20,\
#firozi (v2):pink orange
"#2ff6ea:#ff9a84":35,\
#firozi (v2):indigo (v1)
"#2ff6ea:#c97fff":35,\
#firozi (v2):indigo (v2)
"#2ff6ea:#6e76ff":35,\

#firozi (v3):turquoise
"#49d9ff:#01edd2":7,\
#firozi (v3):medium purple
"#49d9ff:#c66aff":50,\
#firozi (v3):light electric pink (v1)
"#49d9ff:#eb61ff":30,\
#firozi (v3):light electric pink (v2)
"#49d9ff:#fc90ff":35,\
#firozi (v3):electric pink
"#49d9ff:#f574ff":40,\
#firozi (v3):dark electric pink
"#49d9ff:#ff60e1":30,\
#firozi (v3):coral
"#49d9ff:#f88379":40,\
#firozi (v3):purple (v1)
"#49d9ff:#977aff":20,\
#firozi (v3):purple (v2)
"#49d9ff:#a971fc":15,\
#firozi (v3):purple (v3)
"#49d9ff:#b76eff":20,\
#firozi (v3):purple (v4)
"#49d9ff:#d985f7":40,\
#firozi (v3):purple (v5)
"#49d9ff:#7f5fff":20,\
#firozi (v3):purple (v6)
"#49d9ff:#a991ff":10,\
#firozi (v3):purple (v7)
"#49d9ff:#a293ff":20,\
#firozi (v3):pink (v2)
"#49d9ff:#ff7d9c":40,\
#firozi (v3):pink (v3)
"#49d9ff:#fc98bc":50,\
#firozi (v3):reddish (v1)
"#49d9ff:#ff5f5f":40,\
#firozi (v3):reddish (v2)
"#49d9ff:#ff5a5a":45,\
#firozi (v3):tomato
"#49d9ff:#ff8282":40,\
#firozi (v3):greenish yellow
"#49d9ff:#d4d900":45,\
#firozi (v3):greenish
"#49d9ff:#c8ff28":30,\
#firozi (v3):aquamarine (v1)
"#49d9ff:#28ffaa":15,\
#firozi (v3):aquamarine (v2)
"#49d9ff:#00eccb":15,\
#firozi (v3):firozi (v2)
"#49d9ff:#2ff6ea":7,\
#firozi (v3):firozi (v3)
"#49d9ff:#49d9ff":0,\
#firozi (v3):firozi (v4)
"#49d9ff:#31e6ed":5,\
#firozi (v3):dull green
"#49d9ff:#89e46c":20,\
#firozi (v3):mint greenish
"#49d9ff:#9de245":25,\
#firozi (v3):mint green
"#49d9ff:#66ff3a":30,\
#firozi (v3):light mint green
"#49d9ff:#00f0a9":10,\
#firozi (v3):light green
"#49d9ff:#a5ed31":25,\
#firozi (v3):green (v2)
"#49d9ff:#2ff06f":20,\
#firozi (v3):green (v3)
"#49d9ff:#26e99c":15,\
#firozi (v3):green (v4)
"#49d9ff:#42ec72":15,\
#firozi (v3):green (v5)
"#49d9ff:#46ec5c":20,\
#firozi (v3):green (v6)
"#49d9ff:#50f777":15,\
#firozi (v3):green (v7)
"#49d9ff:#01f5a1":15,\
#firozi (v3):green (v8)
"#49d9ff:#42e966":20,\
#firozi (v3):green (v9)
"#49d9ff:#52f578":15,\
#firozi (v3):sky blue (v1)
"#49d9ff:#69baf5":5,\
#firozi (v3):sky blue (v2)
"#49d9ff:#6d9eff":7,\
#firozi (v3):sky blue (v3)
"#49d9ff:#32a8f8":5,\
#firozi (v3):sky blue (v4)
"#49d9ff:#5caeff":5,\
#firozi (v3):sky blue (v5)
"#49d9ff:#7ba6fc":5,\
#firozi (v3):blue
"#49d9ff:#6292ff":7,\
#firozi (v3):sky-teal-blue
"#49d9ff:#28d7ff":5,\
#firozi (v3):purple blue
"#49d9ff:#9380ff":15,\
#firozi (v3):teal-blue (v1)
"#49d9ff:#3bc1f0":1,\
#firozi (v3):teal-blue (v2)
"#49d9ff:#34caf0":1,\
#firozi (v3):teal-blue (v3)
"#49d9ff:#01b0ed":7,\
#firozi (v3):gold (v2)
"#49d9ff:#f9cd48":30,\
#firozi (v3):gold (v3)
"#49d9ff:#fed940":30,\
#firozi (v3):gold (v4)
"#49d9ff:#ffd700":40,\
#firozi (v3):orange (v2)
"#49d9ff:#ffaa5f":30,\
#firozi (v3):light orange
"#49d9ff:#ffae7c":30,\
#firozi (v3):yellow-orange
"#49d9ff:#ffca5f":35,\
#firozi (v3):yellow (v1)
"#49d9ff:#fff03a":30,\
#firozi (v3):yellow (v2)
"#49d9ff:#ebdf59":30,\
#firozi (v3):yellow (v3)
"#49d9ff:#f1e157":30,\
#firozi (v3):pink orange
"#49d9ff:#ff9a84":35,\
#firozi (v3):indigo (v1)
"#49d9ff:#c97fff":20,\
#firozi (v3):indigo (v2)
"#49d9ff:#6e76ff":25,\

#firozi (v4):turquoise
"#31e6ed:#01edd2":1,\
#firozi (v4):medium purple
"#31e6ed:#c66aff":55,\
#firozi (v4):light electric pink (v1)
"#31e6ed:#eb61ff":35,\
#firozi (v4):light electric pink (v2)
"#31e6ed:#fc90ff":35,\
#firozi (v4):electric pink
"#31e6ed:#f574ff":50,\
#firozi (v4):dark electric pink
"#31e6ed:#ff60e1":35,\
#firozi (v4):coral
"#31e6ed:#f88379":50,\
#firozi (v4):purple (v1)
"#31e6ed:#977aff":25,\
#firozi (v4):purple (v2)
"#31e6ed:#a971fc":20,\
#firozi (v4):purple (v3)
"#31e6ed:#b76eff":25,\
#firozi (v4):purple (v4)
"#31e6ed:#d985f7":45,\
#firozi (v4):purple (v5)
"#31e6ed:#7f5fff":25,\
#firozi (v4):purple (v6)
"#31e6ed:#a991ff":15,\
#firozi (v4):purple (v7)
"#31e6ed:#a293ff":25,\
#firozi (v4):pink (v2)
"#31e6ed:#ff7d9c":35,\
#firozi (v4):pink (v3)
"#31e6ed:#fc98bc":55,\
#firozi (v4):reddish (v1)
"#31e6ed:#ff5f5f":45,\
#firozi (v4):reddish (v2)
"#31e6ed:#ff5a5a":50,\
#firozi (v4):tomato
"#31e6ed:#ff8282":45,\
#firozi (v4):greenish yellow
"#31e6ed:#d4d900":40,\
#firozi (v4):greenish
"#31e6ed:#c8ff28":25,\
#firozi (v4):aquamarine (v1)
"#31e6ed:#28ffaa":10,\
#firozi (v4):aquamarine (v2)
"#31e6ed:#00eccb":10,\
#firozi (v4):firozi (v2)
"#31e6ed:#2ff6ea":1,\
#firozi (v4):firozi (v3)
"#31e6ed:#49d9ff":5,\
#firozi (v4):firozi (v4)
"#31e6ed:#31e6ed":0,\
#firozi (v4):dull green
"#31e6ed:#89e46c":15,\
#firozi (v4):mint greenish
"#31e6ed:#9de245":20,\
#firozi (v4):mint green
"#31e6ed:#66ff3a":25,\
#firozi (v4):light mint green
"#31e6ed:#00f0a9":10,\
#firozi (v4):light green
"#31e6ed:#a5ed31":25,\
#firozi (v4):green (v2)
"#31e6ed:#2ff06f":15,\
#firozi (v4):green (v3)
"#31e6ed:#26e99c":10,\
#firozi (v4):green (v4)
"#31e6ed:#42ec72":15,\
#firozi (v4):green (v5)
"#31e6ed:#46ec5c":15,\
#firozi (v4):green (v6)
"#31e6ed:#50f777":10,\
#firozi (v4):green (v7)
"#31e6ed:#01f5a1":7,\
#firozi (v4):green (v8)
"#31e6ed:#42e966":15,\
#firozi (v4):green (v9)
"#31e6ed:#52f578":10,\
#firozi (v4):sky blue (v1)
"#31e6ed:#69baf5":7,\
#firozi (v4):sky blue (v2)
"#31e6ed:#6d9eff":15,\
#firozi (v4):sky blue (v3)
"#31e6ed:#32a8f8":15,\
#firozi (v4):sky blue (v4)
"#31e6ed:#5caeff":7,\
#firozi (v4):sky blue (v5)
"#31e6ed:#7ba6fc":7,\
#firozi (v4):blue
"#31e6ed:#6292ff":20,\
#firozi (v4):sky-teal-blue
"#31e6ed:#28d7ff":1,\
#firozi (v4):purple blue
"#31e6ed:#9380ff":25,\
#firozi (v4):teal-blue (v1)
"#31e6ed:#3bc1f0":1,\
#firozi (v4):teal-blue (v2)
"#31e6ed:#34caf0":1,\
#firozi (v4):teal-blue (v3)
"#31e6ed:#01b0ed":5,\
#firozi (v4):gold (v2)
"#31e6ed:#f9cd48":35,\
#firozi (v4):gold (v3)
"#31e6ed:#fed940":35,\
#firozi (v4):gold (v4)
"#31e6ed:#ffd700":45,\
#firozi (v4):orange (v2)
"#31e6ed:#ffaa5f":40,\
#firozi (v4):light orange
"#31e6ed:#ffae7c":40,\
#firozi (v4):yellow-orange
"#31e6ed:#ffca5f":45,\
#firozi (v4):yellow (v1)
"#31e6ed:#fff03a":35,\
#firozi (v4):yellow (v2)
"#31e6ed:#ebdf59":40,\
#firozi (v4):yellow (v3)
"#31e6ed:#f1e157":40,\
#firozi (v4):pink orange
"#31e6ed:#ff9a84":40,\
#firozi (v4):indigo (v1)
"#31e6ed:#c97fff":50,\
#firozi (v4):indigo (v2)
"#31e6ed:#6e76ff":45,\

#dull green:turquoise
"#89e46c:#01edd2":25,\
#dull green:medium purple
"#89e46c:#c66aff":65,\
#dull green:light electric pink (v1)
"#89e46c:#eb61ff":25,\
#dull green:light electric pink (v2)
"#89e46c:#fc90ff":25,\
#dull green:electric pink
"#89e46c:#f574ff":45,\
#dull green:dark electric pink
"#89e46c:#ff60e1":30,\
#dull green:coral
"#89e46c:#f88379":25,\
#dull green:purple (v1)
"#89e46c:#977aff":30,\
#dull green:purple (v2)
"#89e46c:#a971fc":35,\
#dull green:purple (v3)
"#89e46c:#b76eff":35,\
#dull green:purple (v4)
"#89e46c:#d985f7":25,\
#dull green:purple (v5)
"#89e46c:#7f5fff":40,\
#dull green:purple (v6)
"#89e46c:#a991ff":25,\
#dull green:purple (v7)
"#89e46c:#a293ff":35,\
#dull green:pink (v2)
"#89e46c:#ff7d9c":45,\
#dull green:pink (v3)
"#89e46c:#fc98bc":35,\
#dull green:reddish (v1)
"#89e46c:#ff5f5f":50,\
#dull green:reddish (v2)
"#89e46c:#ff5a5a":35,\
#dull green:tomato
"#89e46c:#ff8282":35,\
#dull green:greenish yellow
"#89e46c:#d4d900":15,\
#dull green:greenish
"#89e46c:#c8ff28":15,\
#dull green:aquamarine (v1)
"#89e46c:#28ffaa":7,\
#dull green:aquamarine (v2)
"#89e46c:#00eccb":15,\
#dull green:firozi (v2)
"#89e46c:#2ff6ea":15,\
#dull green:firozi (v3)
"#89e46c:#49d9ff":20,\
#dull green:firozi (v4)
"#89e46c:#31e6ed":15,\
#dull green:dull green
"#89e46c:#89e46c":0,\
#dull green:mint greenish
"#89e46c:#9de245":5,\
#dull green:mint green
"#89e46c:#66ff3a":5,\
#dull green:light mint green
"#89e46c:#00f0a9":10,\
#dull green:light green
"#89e46c:#a5ed31":7,\
#dull green:green (v2)
"#89e46c:#2ff06f":15,\
#dull green:green (v3)
"#89e46c:#26e99c":15,\
#dull green:green (v4)
"#89e46c:#42ec72":10,\
#dull green:green (v5)
"#89e46c:#46ec5c":7,\
#dull green:green (v6)
"#89e46c:#50f777":5,\
#dull green:green (v7)
"#89e46c:#01f5a1":15,\
#dull green:green (v8)
"#89e46c:#42e966":7,\
#dull green:green (v9)
"#89e46c:#52f578":5,\
#dull green:sky blue (v1)
"#89e46c:#69baf5":45,\
#dull green:sky blue (v2)
"#89e46c:#6d9eff":55,\
#dull green:sky blue (v3)
"#89e46c:#32a8f8":60,\
#dull green:sky blue (v4)
"#89e46c:#5caeff":45,\
#dull green:sky blue (v5)
"#89e46c:#7ba6fc":45,\
#dull green:blue
"#89e46c:#6292ff":55,\
#dull green:sky-teal-blue
"#89e46c:#28d7ff":30,\
#dull green:purple blue
"#89e46c:#9380ff":60,\
#dull green:teal-blue (v1)
"#89e46c:#3bc1f0":30,\
#dull green:teal-blue (v2)
"#89e46c:#34caf0":30,\
#dull green:teal-blue (v3)
"#89e46c:#01b0ed":45,\
#dull green:gold (v2)
"#89e46c:#f9cd48":25,\
#dull green:gold (v3)
"#89e46c:#fed940":20,\
#dull green:gold (v4)
"#89e46c:#ffd700":30,\
#dull green:orange (v2)
"#89e46c:#ffaa5f":40,\
#dull green:light orange
"#89e46c:#ffae7c":40,\
#dull green:yellow-orange
"#89e46c:#ffca5f":25,\
#dull green:yellow (v1)
"#89e46c:#fff03a":20,\
#dull green:yellow (v2)
"#89e46c:#ebdf59":15,\
#dull green:yellow (v3)
"#89e46c:#f1e157":15,\
#dull green:pink orange
"#89e46c:#ff9a84":35,\
#dull green:indigo (v1)
"#89e46c:#c97fff":55,\
#dull green:indigo (v2)
"#89e46c:#6e76ff":65,\

#mint greenish:turquoise
"#9de245:#01edd2":30,\
#mint greenish:medium purple
"#9de245:#c66aff":70,\
#mint greenish:light electric pink (v1)
"#9de245:#eb61ff":45,\
#mint greenish:light electric pink (v2)
"#9de245:#fc90ff":30,\
#mint greenish:electric pink
"#9de245:#f574ff":50,\
#mint greenish:dark electric pink
"#9de245:#ff60e1":35,\
#mint greenish:coral
"#9de245:#f88379":30,\
#mint greenish:purple (v1)
"#9de245:#977aff":35,\
#mint greenish:purple (v2)
"#9de245:#a971fc":40,\
#mint greenish:purple (v3)
"#9de245:#b76eff":40,\
#mint greenish:purple (v4)
"#9de245:#d985f7":30,\
#mint greenish:purple (v5)
"#9de245:#7f5fff":45,\
#mint greenish:purple (v6)
"#9de245:#a991ff":35,\
#mint greenish:purple (v7)
"#9de245:#a293ff":40,\
#mint greenish:pink (v2)
"#9de245:#ff7d9c":50,\
#mint greenish:pink (v3)
"#9de245:#fc98bc":40,\
#mint greenish:reddish (v1)
"#9de245:#ff5f5f":50,\
#mint greenish:reddish (v2)
"#9de245:#ff5a5a":40,\
#mint greenish:tomato
"#9de245:#ff8282":35,\
#mint greenish:greenish yellow
"#9de245:#d4d900":10,\
#mint greenish:greenish
"#9de245:#c8ff28":7,\
#mint greenish:aquamarine (v1)
"#9de245:#28ffaa":10,\
#mint greenish:aquamarine (v2)
"#9de245:#00eccb":15,\
#mint greenish:firozi (v2)
"#9de245:#2ff6ea":20,\
#mint greenish:firozi (v3)
"#9de245:#49d9ff":25,\
#mint greenish:firozi (v4)
"#9de245:#31e6ed":20,\
#mint greenish:dull green
"#9de245:#89e46c":5,\
#mint greenish:mint greenish
"#9de245:#9de245":0,\
#mint greenish:mint green
"#9de245:#66ff3a":7,\
#mint greenish:light mint green
"#9de245:#00f0a9":10,\
#mint greenish:light green
"#9de245:#a5ed31":1,\
#mint greenish:green (v2)
"#9de245:#2ff06f":7,\
#mint greenish:green (v3)
"#9de245:#26e99c":7,\
#mint greenish:green (v4)
"#9de245:#42ec72":5,\
#mint greenish:green (v5)
"#9de245:#46ec5c":5,\
#mint greenish:green (v6)
"#9de245:#50f777":5,\
#mint greenish:green (v7)
"#9de245:#01f5a1":10,\
#mint greenish:green (v8)
"#9de245:#42e966":10,\
#mint greenish:green (v9)
"#9de245:#52f578":7,\
#mint greenish:sky blue (v1)
"#9de245:#69baf5":40,\
#mint greenish:sky blue (v2)
"#9de245:#6d9eff":50,\
#mint greenish:sky blue (v3)
"#9de245:#32a8f8":55,\
#mint greenish:sky blue (v4)
"#9de245:#5caeff":40,\
#mint greenish:sky blue (v5)
"#9de245:#7ba6fc":40,\
#mint greenish:blue
"#9de245:#6292ff":50,\
#mint greenish:sky-teal-blue
"#9de245:#28d7ff":35,\
#mint greenish:purple blue
"#9de245:#9380ff":45,\
#mint greenish:teal-blue (v1)
"#9de245:#3bc1f0":50,\
#mint greenish:teal-blue (v2)
"#9de245:#34caf0":50,\
#mint greenish:teal-blue (v3)
"#9de245:#01b0ed":60,\
#mint greenish:gold (v2)
"#9de245:#f9cd48":40,\
#mint greenish:gold (v3)
"#9de245:#fed940":40,\
#mint greenish:gold (v4)
"#9de245:#ffd700":45,\
#mint greenish:orange (v2)
"#9de245:#ffaa5f":25,\
#mint greenish:light orange
"#9de245:#ffae7c":25,\
#mint greenish:yellow-orange
"#9de245:#ffca5f":15,\
#mint greenish:yellow (v1)
"#9de245:#fff03a":10,\
#mint greenish:yellow (v2)
"#9de245:#ebdf59":7,\
#mint greenish:yellow (v3)
"#9de245:#f1e157":7,\
#mint greenish:pink orange
"#9de245:#ff9a84":25,\
#mint greenish:indigo (v1)
"#9de245:#c97fff":45,\
#mint greenish:indigo (v2)
"#9de245:#6e76ff":50,\

#mint green:turquoise
"#66ff3a:#01edd2":30,\
#mint green:medium purple
"#66ff3a:#c66aff":80,\
#mint green:light electric pink (v1)
"#66ff3a:#eb61ff":70,\
#mint green:light electric pink (v2)
"#66ff3a:#fc90ff":65,\
#mint green:electric pink
"#66ff3a:#f574ff":70,\
#mint green:dark electric pink
"#66ff3a:#ff60e1":55,\
#mint green:coral
"#66ff3a:#f88379":45,\
#mint green:purple (v1)
"#66ff3a:#977aff":45,\
#mint green:purple (v2)
"#66ff3a:#a971fc":50,\
#mint green:purple (v3)
"#66ff3a:#b76eff":55,\
#mint green:purple (v4)
"#66ff3a:#d985f7":50,\
#mint green:purple (v5)
"#66ff3a:#7f5fff":75,\
#mint green:purple (v6)
"#66ff3a:#a991ff":55,\
#mint green:purple (v7)
"#66ff3a:#a293ff":50,\
#mint green:pink (v2)
"#66ff3a:#ff7d9c":60,\
#mint green:pink (v3)
"#66ff3a:#fc98bc":55,\
#mint green:reddish (v1)
"#66ff3a:#ff5f5f":60,\
#mint green:reddish (v2)
"#66ff3a:#ff5a5a":50,\
#mint green:tomato
"#66ff3a:#ff8282":55,\
#mint green:greenish yellow
"#66ff3a:#d4d900":15,\
#mint green:greenish
"#66ff3a:#c8ff28":7,\
#mint green:aquamarine (v1)
"#66ff3a:#28ffaa":15,\
#mint green:aquamarine (v2)
"#66ff3a:#00eccb":15,\
#mint green:firozi (v2)
"#66ff3a:#2ff6ea":25,\
#mint green:firozi (v3)
"#66ff3a:#49d9ff":30,\
#mint green:firozi (v4)
"#66ff3a:#31e6ed":25,\
#mint green:dull green
"#66ff3a:#89e46c":5,\
#mint green:mint greenish
"#66ff3a:#9de245":7,\
#mint green:mint green
"#66ff3a:#66ff3a":0,\
#mint green:light mint green
"#66ff3a:#00f0a9":10,\
#mint green:light green
"#66ff3a:#a5ed31":7,\
#mint green:green (v2)
"#66ff3a:#2ff06f":7,\
#mint green:green (v3)
"#66ff3a:#26e99c":10,\
#mint green:green (v4)
"#66ff3a:#42ec72":5,\
#mint green:green (v5)
"#66ff3a:#46ec5c":5,\
#mint green:green (v6)
"#66ff3a:#50f777":5,\
#mint green:green (v7)
"#66ff3a:#01f5a1":10,\
#mint green:green (v8)
"#66ff3a:#42e966":7,\
#mint green:green (v9)
"#66ff3a:#52f578":5,\
#mint green:sky blue (v1)
"#66ff3a:#69baf5":40,\
#mint green:sky blue (v2)
"#66ff3a:#6d9eff":50,\
#mint green:sky blue (v3)
"#66ff3a:#32a8f8":60,\
#mint green:sky blue (v4)
"#66ff3a:#5caeff":50,\
#mint green:sky blue (v5)
"#66ff3a:#7ba6fc":50,\
#mint green:blue
"#66ff3a:#6292ff":70,\
#mint green:sky-teal-blue
"#66ff3a:#28d7ff":35,\
#mint green:purple blue
"#66ff3a:#9380ff":70,\
#mint green:teal-blue (v1)
"#66ff3a:#3bc1f0":40,\
#mint green:teal-blue (v2)
"#66ff3a:#34caf0":40,\
#mint green:teal-blue (v3)
"#66ff3a:#01b0ed":60,\
#mint green:gold (v2)
"#66ff3a:#f9cd48":25,\
#mint green:gold (v3)
"#66ff3a:#fed940":20,\
#mint green:gold (v4)
"#66ff3a:#ffd700":25,\
#mint green:orange (v2)
"#66ff3a:#ffaa5f":25,\
#mint green:light orange
"#66ff3a:#ffae7c":25,\
#mint green:yellow-orange
"#66ff3a:#ffca5f":20,\
#mint green:yellow (v1)
"#66ff3a:#fff03a":10,\
#mint green:yellow (v2)
"#66ff3a:#ebdf59":15,\
#mint green:yellow (v3)
"#66ff3a:#f1e157":15,\
#mint green:pink orange
"#66ff3a:#ff9a84":30,\
#mint green:indigo (v1)
"#66ff3a:#c97fff":50,\
#mint green:indigo (v2)
"#66ff3a:#6e76ff":70,\

#light mint green:turquoise
"#00f0a9:#01edd2":5,\
#light mint green:medium purple
"#00f0a9:#c66aff":80,\
#light mint green:light electric pink (v1)
"#00f0a9:#eb61ff":75,\
#light mint green:light electric pink (v2)
"#00f0a9:#fc90ff":55,\
#light mint green:electric pink
"#00f0a9:#f574ff":60,\
#light mint green:dark electric pink
"#00f0a9:#ff60e1":45,\
#light mint green:coral
"#00f0a9:#f88379":45,\
#light mint green:purple (v1)
"#00f0a9:#977aff":25,\
#light mint green:purple (v2)
"#00f0a9:#a971fc":35,\
#light mint green:purple (v3)
"#00f0a9:#b76eff":45,\
#light mint green:purple (v4)
"#00f0a9:#d985f7":45,\
#light mint green:purple (v5)
"#00f0a9:#7f5fff":40,\
#light mint green:purple (v6)
"#00f0a9:#a991ff":30,\
#light mint green:purple (v7)
"#00f0a9:#a293ff":40,\
#light mint green:pink (v2)
"#00f0a9:#ff7d9c":55,\
#light mint green:pink (v3)
"#00f0a9:#fc98bc":50,\
#light mint green:reddish (v1)
"#00f0a9:#ff5f5f":45,\
#light mint green:reddish (v2)
"#00f0a9:#ff5a5a":45,\
#light mint green:tomato
"#00f0a9:#ff8282":45,\
#light mint green:greenish yellow
"#00f0a9:#d4d900":30,\
#light mint green:greenish
"#00f0a9:#c8ff28":20,\
#light mint green:aquamarine (v1)
"#00f0a9:#28ffaa":1,\
#light mint green:aquamarine (v2)
"#00f0a9:#00eccb":5,\
#light mint green:firozi (v2)
"#00f0a9:#2ff6ea":5,\
#light mint green:firozi (v3)
"#00f0a9:#49d9ff":10,\
#light mint green:firozi (v4)
"#00f0a9:#31e6ed":10,\
#light mint green:dull green
"#00f0a9:#89e46c":10,\
#light mint green:mint greenish
"#00f0a9:#9de245":10,\
#light mint green:mint green
"#00f0a9:#66ff3a":10,\
#light mint green:light mint green
"#00f0a9:#00f0a9":0,\
#light mint green:light green
"#00f0a9:#a5ed31":15,\
#light mint green:green (v2)
"#00f0a9:#2ff06f":5,\
#light mint green:green (v3)
"#00f0a9:#26e99c":1,\
#light mint green:green (v4)
"#00f0a9:#42ec72":5,\
#light mint green:green (v5)
"#00f0a9:#46ec5c":7,\
#light mint green:green (v6)
"#00f0a9:#50f777":5,\
#light mint green:green (v7)
"#00f0a9:#01f5a1":1,\
#light mint green:green (v8)
"#00f0a9:#42e966":5,\
#light mint green:green (v9)
"#00f0a9:#52f578":5,\
#light mint green:sky blue (v1)
"#00f0a9:#69baf5":25,\
#light mint green:sky blue (v2)
"#00f0a9:#6d9eff":35,\
#light mint green:sky blue (v3)
"#00f0a9:#32a8f8":35,\
#light mint green:sky blue (v4)
"#00f0a9:#5caeff":30,\
#light mint green:sky blue (v5)
"#00f0a9:#7ba6fc":30,\
#light mint green:blue
"#00f0a9:#6292ff":50,\
#light mint green:sky-teal-blue
"#00f0a9:#28d7ff":15,\
#light mint green:purple blue
"#00f0a9:#9380ff":35,\
#light mint green:teal-blue (v1)
"#00f0a9:#3bc1f0":20,\
#light mint green:teal-blue (v2)
"#00f0a9:#34caf0":20,\
#light mint green:teal-blue (v3)
"#00f0a9:#01b0ed":30,\
#light mint green:gold (v2)
"#00f0a9:#f9cd48":45,\
#light mint green:gold (v3)
"#00f0a9:#fed940":45,\
#light mint green:gold (v4)
"#00f0a9:#ffd700":55,\
#light mint green:orange (v2)
"#00f0a9:#ffaa5f":40,\
#light mint green:light orange
"#00f0a9:#ffae7c":35,\
#light mint green:yellow-orange
"#00f0a9:#ffca5f":35,\
#light mint green:yellow (v1)
"#00f0a9:#fff03a":25,\
#light mint green:yellow (v2)
"#00f0a9:#ebdf59":30,\
#light mint green:yellow (v3)
"#00f0a9:#f1e157":30,\
#light mint green:pink orange
"#00f0a9:#ff9a84":45,\
#light mint green:indigo (v1)
"#00f0a9:#c97fff":55,\
#light mint green:indigo (v2)
"#00f0a9:#6e76ff":55,\

#light green:turquoise
"#a5ed31:#01edd2":20,\
#light green:medium purple
"#a5ed31:#c66aff":70,\
#light green:light electric pink (v1)
"#a5ed31:#eb61ff":55,\
#light green:light electric pink (v2)
"#a5ed31:#fc90ff":60,\
#light green:electric pink
"#a5ed31:#f574ff":65,\
#light green:dark electric pink
"#a5ed31:#ff60e1":40,\
#light green:coral
"#a5ed31:#f88379":25,\
#light green:purple (v1)
"#a5ed31:#977aff":35,\
#light green:purple (v2)
"#a5ed31:#a971fc":45,\
#light green:purple (v3)
"#a5ed31:#b76eff":50,\
#light green:purple (v4)
"#a5ed31:#d985f7":50,\
#light green:purple (v5)
"#a5ed31:#7f5fff":50,\
#light green:purple (v6)
"#a5ed31:#a991ff":40,\
#light green:purple (v7)
"#a5ed31:#a293ff":50,\
#light green:pink (v2)
"#a5ed31:#ff7d9c":45,\
#light green:pink (v3)
"#a5ed31:#fc98bc":55,\
#light green:reddish (v1)
"#a5ed31:#ff5f5f":50,\
#light green:reddish (v2)
"#a5ed31:#ff5a5a":40,\
#light green:tomato
"#a5ed31:#ff8282":30,\
#light green:greenish yellow
"#a5ed31:#d4d900":7,\
#light green:greenish
"#a5ed31:#c8ff28":1,\
#light green:aquamarine (v1)
"#a5ed31:#28ffaa":15,\
#light green:aquamarine (v2)
"#a5ed31:#00eccb":15,\
#light green:firozi (v2)
"#a5ed31:#2ff6ea":20,\
#light green:firozi (v3)
"#a5ed31:#49d9ff":25,\
#light green:firozi (v4)
"#a5ed31:#31e6ed":25,\
#light green:dull green
"#a5ed31:#89e46c":7,\
#light green:mint greenish
"#a5ed31:#9de245":1,\
#light green:mint green
"#a5ed31:#66ff3a":7,\
#light green:light mint green
"#a5ed31:#00f0a9":15,\
#light green:light green
"#a5ed31:#a5ed31":0,\
#light green:green (v2)
"#a5ed31:#2ff06f":10,\
#light green:green (v3)
"#a5ed31:#26e99c":10,\
#light green:green (v4)
"#a5ed31:#42ec72":5,\
#light green:green (v5)
"#a5ed31:#46ec5c":5,\
#light green:green (v6)
"#a5ed31:#50f777":5,\
#light green:green (v7)
"#a5ed31:#01f5a1":15,\
#light green:green (v8)
"#a5ed31:#42e966":10,\
#light green:green (v9)
"#a5ed31:#52f578":7,\
#light green:sky blue (v1)
"#a5ed31:#69baf5":30,\
#light green:sky blue (v2)
"#a5ed31:#6d9eff":35,\
#light green:sky blue (v3)
"#a5ed31:#32a8f8":45,\
#light green:sky blue (v4)
"#a5ed31:#5caeff":40,\
#light green:sky blue (v5)
"#a5ed31:#7ba6fc":35,\
#light green:blue
"#a5ed31:#6292ff":55,\
#light green:sky-teal-blue
"#a5ed31:#28d7ff":35,\
#light green:purple blue
"#a5ed31:#9380ff":55,\
#light green:teal-blue (v1)
"#a5ed31:#3bc1f0":40,\
#light green:teal-blue (v2)
"#a5ed31:#34caf0":40,\
#light green:teal-blue (v3)
"#a5ed31:#01b0ed":65,\
#light green:gold (v2)
"#a5ed31:#f9cd48":20,\
#light green:gold (v3)
"#a5ed31:#fed940":20,\
#light green:gold (v4)
"#a5ed31:#ffd700":25,\
#light green:orange (v2)
"#a5ed31:#ffaa5f":25,\
#light green:light orange
"#a5ed31:#ffae7c":25,\
#light green:yellow-orange
"#a5ed31:#ffca5f":15,\
#light green:yellow (v1)
"#a5ed31:#fff03a":5,\
#light green:yellow (v2)
"#a5ed31:#ebdf59":7,\
#light green:yellow (v3)
"#a5ed31:#f1e157":10,\
#light green:pink orange
"#a5ed31:#ff9a84":25,\
#light green:indigo (v1)
"#a5ed31:#c97fff":45,\
#light green:indigo (v2)
"#a5ed31:#6e76ff":55,\

#green (v2):turquoise
"#2ff06f:#01edd2":15,\
#green (v2):medium purple
"#2ff06f:#c66aff":75,\
#green (v2):light electric pink (v1)
"#2ff06f:#eb61ff":65,\
#green (v2):light electric pink (v2)
"#2ff06f:#fc90ff":70,\
#green (v2):electric pink
"#2ff06f:#f574ff":40,\
#green (v2):dark electric pink
"#2ff06f:#ff60e1":40,\
#green (v2):coral
"#2ff06f:#f88379":35,\
#green (v2):purple (v1)
"#2ff06f:#977aff":30,\
#green (v2):purple (v2)
"#2ff06f:#a971fc":40,\
#green (v2):purple (v3)
"#2ff06f:#b76eff":40,\
#green (v2):purple (v4)
"#2ff06f:#d985f7":45,\
#green (v2):purple (v5)
"#2ff06f:#7f5fff":55,\
#green (v2):purple (v6)
"#2ff06f:#a991ff":35,\
#green (v2):purple (v7)
"#2ff06f:#a293ff":35,\
#green (v2):pink (v2)
"#2ff06f:#ff7d9c":40,\
#green (v2):pink (v3)
"#2ff06f:#fc98bc":50,\
#green (v2):reddish (v1)
"#2ff06f:#ff5f5f":40,\
#green (v2):reddish (v2)
"#2ff06f:#ff5a5a":40,\
#green (v2):tomato
"#2ff06f:#ff8282":40,\
#green (v2):greenish yellow
"#2ff06f:#d4d900":25,\
#green (v2):greenish
"#2ff06f:#c8ff28":15,\
#green (v2):aquamarine (v1)
"#2ff06f:#28ffaa":5,\
#green (v2):aquamarine (v2)
"#2ff06f:#00eccb":5,\
#green (v2):firozi (v2)
"#2ff06f:#2ff6ea":15,\
#green (v2):firozi (v3)
"#2ff06f:#49d9ff":20,\
#green (v2):firozi (v4)
"#2ff06f:#31e6ed":15,\
#green (v2):dull green
"#2ff06f:#89e46c":15,\
#green (v2):mint greenish
"#2ff06f:#9de245":7,\
#green (v2):mint green
"#2ff06f:#66ff3a":7,\
#green (v2):light mint green
"#2ff06f:#00f0a9":5,\
#green (v2):light green
"#2ff06f:#a5ed31":10,\
#green (v2):green (v2)
"#2ff06f:#2ff06f":0,\
#green (v2):green (v3)
"#2ff06f:#26e99c":10,\
#green (v2):green (v4)
"#2ff06f:#42ec72":1,\
#green (v2):green (v5)
"#2ff06f:#46ec5c":1,\
#green (v2):green (v6)
"#2ff06f:#50f777":1,\
#green (v2):green (v7)
"#2ff06f:#01f5a1":5,\
#green (v2):green (v8)
"#2ff06f:#42e966":1,\
#green (v2):green (v9)
"#2ff06f:#52f578":1,\
#green (v2):sky blue (v1)
"#2ff06f:#69baf5":25,\
#green (v2):sky blue (v2)
"#2ff06f:#6d9eff":30,\
#green (v2):sky blue (v3)
"#2ff06f:#32a8f8":45,\
#green (v2):sky blue (v4)
"#2ff06f:#5caeff":25,\
#green (v2):sky blue (v5)
"#2ff06f:#7ba6fc":25,\
#green (v2):blue
"#2ff06f:#6292ff":45,\
#green (v2):sky-teal-blue
"#2ff06f:#28d7ff":30,\
#green (v2):purple blue
"#2ff06f:#9380ff":45,\
#green (v2):teal-blue (v1)
"#2ff06f:#3bc1f0":30,\
#green (v2):teal-blue (v2)
"#2ff06f:#34caf0":30,\
#green (v2):teal-blue (v3)
"#2ff06f:#01b0ed":45,\
#green (v2):gold (v2)
"#2ff06f:#f9cd48":30,\
#green (v2):gold (v3)
"#2ff06f:#fed940":25,\
#green (v2):gold (v4)
"#2ff06f:#ffd700":35,\
#green (v2):orange (v2)
"#2ff06f:#ffaa5f":30,\
#green (v2):light orange
"#2ff06f:#ffae7c":30,\
#green (v2):yellow-orange
"#2ff06f:#ffca5f":30,\
#green (v2):yellow (v1)
"#2ff06f:#fff03a":25,\
#green (v2):yellow (v2)
"#2ff06f:#ebdf59":20,\
#green (v2):yellow (v3)
"#2ff06f:#f1e157":20,\
#green (v2):pink orange
"#2ff06f:#ff9a84":35,\
#green (v2):indigo (v1)
"#2ff06f:#c97fff":45,\
#green (v2):indigo (v2)
"#2ff06f:#6e76ff":60,\

#green (v3):turquoise
"#26e99c:#01edd2":5,\
#green (v3):medium purple
"#26e99c:#c66aff":65,\
#green (v3):light electric pink (v1)
"#26e99c:#eb61ff":45,\
#green (v3):light electric pink (v2)
"#26e99c:#fc90ff":50,\
#green (v3):electric pink
"#26e99c:#f574ff":30,\
#green (v3):dark electric pink
"#26e99c:#ff60e1":35,\
#green (v3):coral
"#26e99c:#f88379":30,\
#green (v3):purple (v1)
"#26e99c:#977aff":30,\
#green (v3):purple (v2)
"#26e99c:#a971fc":35,\
#green (v3):purple (v3)
"#26e99c:#b76eff":35,\
#green (v3):purple (v4)
"#26e99c:#d985f7":40,\
#green (v3):purple (v5)
"#26e99c:#7f5fff":40,\
#green (v3):purple (v6)
"#26e99c:#a991ff":30,\
#green (v3):purple (v7)
"#26e99c:#a293ff":25,\
#green (v3):pink (v2)
"#26e99c:#ff7d9c":45,\
#green (v3):pink (v3)
"#26e99c:#fc98bc":50,\
#green (v3):reddish (v1)
"#26e99c:#ff5f5f":40,\
#green (v3):reddish (v2)
"#26e99c:#ff5a5a":40,\
#green (v3):tomato
"#26e99c:#ff8282":40,\
#green (v3):greenish yellow
"#26e99c:#d4d900":20,\
#green (v3):greenish
"#26e99c:#c8ff28":15,\
#green (v3):aquamarine (v1)
"#26e99c:#28ffaa":1,\
#green (v3):aquamarine (v2)
"#26e99c:#00eccb":1,\
#green (v3):firozi (v2)
"#26e99c:#2ff6ea":5,\
#green (v3):firozi (v3)
"#26e99c:#49d9ff":15,\
#green (v3):firozi (v4)
"#26e99c:#31e6ed":10,\
#green (v3):dull green
"#26e99c:#89e46c":15,\
#green (v3):mint greenish
"#26e99c:#9de245":7,\
#green (v3):mint green
"#26e99c:#66ff3a":10,\
#green (v3):light mint green
"#26e99c:#00f0a9":1,\
#green (v3):light green
"#26e99c:#a5ed31":10,\
#green (v3):green (v2)
"#26e99c:#2ff06f":10,\
#green (v3):green (v3)
"#26e99c:#26e99c":0,\
#green (v3):green (v4)
"#26e99c:#42ec72":5,\
#green (v3):green (v5)
"#26e99c:#46ec5c":5,\
#green (v3):green (v6)
"#26e99c:#50f777":5,\
#green (v3):green (v7)
"#26e99c:#01f5a1":1,\
#green (v3):green (v8)
"#26e99c:#42e966":5,\
#green (v3):green (v9)
"#26e99c:#52f578":5,\
#green (v3):sky blue (v1)
"#26e99c:#69baf5":30,\
#green (v3):sky blue (v2)
"#26e99c:#6d9eff":40,\
#green (v3):sky blue (v3)
"#26e99c:#32a8f8":50,\
#green (v3):sky blue (v4)
"#26e99c:#5caeff":40,\
#green (v3):sky blue (v5)
"#26e99c:#7ba6fc":40,\
#green (v3):blue
"#26e99c:#6292ff":50,\
#green (v3):sky-teal-blue
"#26e99c:#28d7ff":30,\
#green (v3):purple blue
"#26e99c:#9380ff":45,\
#green (v3):teal-blue (v1)
"#26e99c:#3bc1f0":35,\
#green (v3):teal-blue (v2)
"#26e99c:#34caf0":35,\
#green (v3):teal-blue (v3)
"#26e99c:#01b0ed":45,\
#green (v3):gold (v2)
"#26e99c:#f9cd48":40,\
#green (v3):gold (v3)
"#26e99c:#fed940":40,\
#green (v3):gold (v4)
"#26e99c:#ffd700":50,\
#green (v3):orange (v2)
"#26e99c:#ffaa5f":25,\
#green (v3):light orange
"#26e99c:#ffae7c":25,\
#green (v3):yellow-orange
"#26e99c:#ffca5f":30,\
#green (v3):yellow (v1)
"#26e99c:#fff03a":30,\
#green (v3):yellow (v2)
"#26e99c:#ebdf59":35,\
#green (v3):yellow (v3)
"#26e99c:#f1e157":35,\
#green (v3):pink orange
"#26e99c:#ff9a84":40,\
#green (v3):indigo (v1)
"#26e99c:#c97fff":50,\
#green (v3):indigo (v2)
"#26e99c:#6e76ff":60,\

#green (v4):turquoise
"#42ec72:#01edd2":10,\
#green (v4):medium purple
"#42ec72:#c66aff":70,\
#green (v4):light electric pink (v1)
"#42ec72:#eb61ff":55,\
#green (v4):light electric pink (v2)
"#42ec72:#fc90ff":55,\
#green (v4):electric pink
"#42ec72:#f574ff":30,\
#green (v4):dark electric pink
"#42ec72:#ff60e1":35,\
#green (v4):coral
"#42ec72:#f88379":35,\
#green (v4):purple (v1)
"#42ec72:#977aff":35,\
#green (v4):purple (v2)
"#42ec72:#a971fc":35,\
#green (v4):purple (v3)
"#42ec72:#b76eff":35,\
#green (v4):purple (v4)
"#42ec72:#d985f7":45,\
#green (v4):purple (v5)
"#42ec72:#7f5fff":45,\
#green (v4):purple (v6)
"#42ec72:#a991ff":40,\
#green (v4):purple (v7)
"#42ec72:#a293ff":30,\
#green (v4):pink (v2)
"#42ec72:#ff7d9c":50,\
#green (v4):pink (v3)
"#42ec72:#fc98bc":55,\
#green (v4):reddish (v1)
"#42ec72:#ff5f5f":40,\
#green (v4):reddish (v2)
"#42ec72:#ff5a5a":45,\
#green (v4):tomato
"#42ec72:#ff8282":45,\
#green (v4):greenish yellow
"#42ec72:#d4d900":20,\
#green (v4):greenish
"#42ec72:#c8ff28":15,\
#green (v4):aquamarine (v1)
"#42ec72:#28ffaa":5,\
#green (v4):aquamarine (v2)
"#42ec72:#00eccb":10,\
#green (v4):firozi (v2)
"#42ec72:#2ff6ea":10,\
#green (v4):firozi (v3)
"#42ec72:#49d9ff":15,\
#green (v4):firozi (v4)
"#42ec72:#31e6ed":15,\
#green (v4):dull green
"#42ec72:#89e46c":10,\
#green (v4):mint greenish
"#42ec72:#9de245":5,\
#green (v4):mint green
"#42ec72:#66ff3a":5,\
#green (v4):light mint green
"#42ec72:#00f0a9":5,\
#green (v4):light green
"#42ec72:#a5ed31":5,\
#green (v4):green (v2)
"#42ec72:#2ff06f":1,\
#green (v4):green (v3)
"#42ec72:#26e99c":5,\
#green (v4):green (v4)
"#42ec72:#42ec72":0,\
#green (v4):green (v5)
"#42ec72:#46ec5c":1,\
#green (v4):green (v6)
"#42ec72:#50f777":1,\
#green (v4):green (v7)
"#42ec72:#01f5a1":7,\
#green (v4):green (v8)
"#42ec72:#42e966":1,\
#green (v4):green (v9)
"#42ec72:#52f578":1,\
#green (v4):sky blue (v1)
"#42ec72:#69baf5":35,\
#green (v4):sky blue (v2)
"#42ec72:#6d9eff":45,\
#green (v4):sky blue (v3)
"#42ec72:#32a8f8":50,\
#green (v4):sky blue (v4)
"#42ec72:#5caeff":40,\
#green (v4):sky blue (v5)
"#42ec72:#7ba6fc":40,\
#green (v4):blue
"#42ec72:#6292ff":60,\
#green (v4):sky-teal-blue
"#42ec72:#28d7ff":35,\
#green (v4):purple blue
"#42ec72:#9380ff":50,\
#green (v4):teal-blue (v1)
"#42ec72:#3bc1f0":30,\
#green (v4):teal-blue (v2)
"#42ec72:#34caf0":30,\
#green (v4):teal-blue (v3)
"#42ec72:#01b0ed":60,\
#green (v4):gold (v2)
"#42ec72:#f9cd48":25,\
#green (v4):gold (v3)
"#42ec72:#fed940":20,\
#green (v4):gold (v4)
"#42ec72:#ffd700":35,\
#green (v4):orange (v2)
"#42ec72:#ffaa5f":25,\
#green (v4):light orange
"#42ec72:#ffae7c":25,\
#green (v4):yellow-orange
"#42ec72:#ffca5f":20,\
#green (v4):yellow (v1)
"#42ec72:#fff03a":15,\
#green (v4):yellow (v2)
"#42ec72:#ebdf59":20,\
#green (v4):yellow (v3)
"#42ec72:#f1e157":20,\
#green (v4):pink orange
"#42ec72:#ff9a84":35,\
#green (v4):indigo (v1)
"#42ec72:#c97fff":55,\
#green (v4):indigo (v2)
"#42ec72:#6e76ff":75,\

#green (v5):turquoise
"#46ec5c:#01edd2":10,\
#green (v5):medium purple
"#46ec5c:#c66aff":70,\
#green (v5):light electric pink (v1)
"#46ec5c:#eb61ff":55,\
#green (v5):light electric pink (v2)
"#46ec5c:#fc90ff":55,\
#green (v5):electric pink
"#46ec5c:#f574ff":35,\
#green (v5):dark electric pink
"#46ec5c:#ff60e1":40,\
#green (v5):coral
"#46ec5c:#f88379":35,\
#green (v5):purple (v1)
"#46ec5c:#977aff":35,\
#green (v5):purple (v2)
"#46ec5c:#a971fc":35,\
#green (v5):purple (v3)
"#46ec5c:#b76eff":35,\
#green (v5):purple (v4)
"#46ec5c:#d985f7":50,\
#green (v5):purple (v5)
"#46ec5c:#7f5fff":45,\
#green (v5):purple (v6)
"#46ec5c:#a991ff":45,\
#green (v5):purple (v7)
"#46ec5c:#a293ff":30,\
#green (v5):pink (v2)
"#46ec5c:#ff7d9c":60,\
#green (v5):pink (v3)
"#46ec5c:#fc98bc":55,\
#green (v5):reddish (v1)
"#46ec5c:#ff5f5f":40,\
#green (v5):reddish (v2)
"#46ec5c:#ff5a5a":45,\
#green (v5):tomato
"#46ec5c:#ff8282":45,\
#green (v5):greenish yellow
"#46ec5c:#d4d900":15,\
#green (v5):greenish
"#46ec5c:#c8ff28":10,\
#green (v5):aquamarine (v1)
"#46ec5c:#28ffaa":7,\
#green (v5):aquamarine (v2)
"#46ec5c:#00eccb":10,\
#green (v5):firozi (v2)
"#46ec5c:#2ff6ea":10,\
#green (v5):firozi (v3)
"#46ec5c:#49d9ff":20,\
#green (v5):firozi (v4)
"#46ec5c:#31e6ed":15,\
#green (v5):dull green
"#46ec5c:#89e46c":7,\
#green (v5):mint greenish
"#46ec5c:#9de245":5,\
#green (v5):mint green
"#46ec5c:#66ff3a":5,\
#green (v5):light mint green
"#46ec5c:#00f0a9":7,\
#green (v5):light green
"#46ec5c:#a5ed31":5,\
#green (v5):green (v2)
"#46ec5c:#2ff06f":1,\
#green (v5):green (v3)
"#46ec5c:#26e99c":5,\
#green (v5):green (v4)
"#46ec5c:#42ec72":1,\
#green (v5):green (v5)
"#46ec5c:#46ec5c":0,\
#green (v5):green (v6)
"#46ec5c:#50f777":5,\
#green (v5):green (v7)
"#46ec5c:#01f5a1":10,\
#green (v5):green (v8)
"#46ec5c:#42e966":1,\
#green (v5):green (v9)
"#46ec5c:#52f578":1,\
#green (v5):sky blue (v1)
"#46ec5c:#69baf5":35,\
#green (v5):sky blue (v2)
"#46ec5c:#6d9eff":45,\
#green (v5):sky blue (v3)
"#46ec5c:#32a8f8":50,\
#green (v5):sky blue (v4)
"#46ec5c:#5caeff":40,\
#green (v5):sky blue (v5)
"#46ec5c:#7ba6fc":40,\
#green (v5):blue
"#46ec5c:#6292ff":55,\
#green (v5):sky-teal-blue
"#46ec5c:#28d7ff":30,\
#green (v5):purple blue
"#46ec5c:#9380ff":55,\
#green (v5):teal-blue (v1)
"#46ec5c:#3bc1f0":35,\
#green (v5):teal-blue (v2)
"#46ec5c:#34caf0":35,\
#green (v5):teal-blue (v3)
"#46ec5c:#01b0ed":50,\
#green (v5):gold (v2)
"#46ec5c:#f9cd48":30,\
#green (v5):gold (v3)
"#46ec5c:#fed940":30,\
#green (v5):gold (v4)
"#46ec5c:#ffd700":40,\
#green (v5):orange (v2)
"#46ec5c:#ffaa5f":35,\
#green (v5):light orange
"#46ec5c:#ffae7c":35,\
#green (v5):yellow-orange
"#46ec5c:#ffca5f":25,\
#green (v5):yellow (v1)
"#46ec5c:#fff03a":20,\
#green (v5):yellow (v2)
"#46ec5c:#ebdf59":20,\
#green (v5):yellow (v3)
"#46ec5c:#f1e157":20,\
#green (v5):pink orange
"#46ec5c:#ff9a84":45,\
#green (v5):indigo (v1)
"#46ec5c:#c97fff":55,\
#green (v5):indigo (v2)
"#46ec5c:#6e76ff":75,\

#green (v6):turquoise
"#50f777:#01edd2":7,\
#green (v6):medium purple
"#50f777:#c66aff":60,\
#green (v6):light electric pink (v1)
"#50f777:#eb61ff":35,\
#green (v6):light electric pink (v2)
"#50f777:#fc90ff":40,\
#green (v6):electric pink
"#50f777:#f574ff":25,\
#green (v6):dark electric pink
"#50f777:#ff60e1":30,\
#green (v6):coral
"#50f777:#f88379":25,\
#green (v6):purple (v1)
"#50f777:#977aff":25,\
#green (v6):purple (v2)
"#50f777:#a971fc":30,\
#green (v6):purple (v3)
"#50f777:#b76eff":30,\
#green (v6):purple (v4)
"#50f777:#d985f7":45,\
#green (v6):purple (v5)
"#50f777:#7f5fff":40,\
#green (v6):purple (v6)
"#50f777:#a991ff":35,\
#green (v6):purple (v7)
"#50f777:#a293ff":25,\
#green (v6):pink (v2)
"#50f777:#ff7d9c":50,\
#green (v6):pink (v3)
"#50f777:#fc98bc":45,\
#green (v6):reddish (v1)
"#50f777:#ff5f5f":40,\
#green (v6):reddish (v2)
"#50f777:#ff5a5a":40,\
#green (v6):tomato
"#50f777:#ff8282":40,\
#green (v6):greenish yellow
"#50f777:#d4d900":20,\
#green (v6):greenish
"#50f777:#c8ff28":15,\
#green (v6):aquamarine (v1)
"#50f777:#28ffaa":5,\
#green (v6):aquamarine (v2)
"#50f777:#00eccb":7,\
#green (v6):firozi (v2)
"#50f777:#2ff6ea":7,\
#green (v6):firozi (v3)
"#50f777:#49d9ff":15,\
#green (v6):firozi (v4)
"#50f777:#31e6ed":10,\
#green (v6):dull green
"#50f777:#89e46c":5,\
#green (v6):mint greenish
"#50f777:#9de245":5,\
#green (v6):mint green
"#50f777:#66ff3a":5,\
#green (v6):light mint green
"#50f777:#00f0a9":5,\
#green (v6):light green
"#50f777:#a5ed31":5,\
#green (v6):green (v2)
"#50f777:#2ff06f":1,\
#green (v6):green (v3)
"#50f777:#26e99c":5,\
#green (v6):green (v4)
"#50f777:#42ec72":1,\
#green (v6):green (v5)
"#50f777:#46ec5c":5,\
#green (v6):green (v6)
"#50f777:#50f777":0,\
#green (v6):green (v7)
"#50f777:#01f5a1":7,\
#green (v6):green (v8)
"#50f777:#42e966":1,\
#green (v6):green (v9)
"#50f777:#52f578":1,\
#green (v6):sky blue (v1)
"#50f777:#69baf5":30,\
#green (v6):sky blue (v2)
"#50f777:#6d9eff":40,\
#green (v6):sky blue (v3)
"#50f777:#32a8f8":45,\
#green (v6):sky blue (v4)
"#50f777:#5caeff":40,\
#green (v6):sky blue (v5)
"#50f777:#7ba6fc":40,\
#green (v6):blue
"#50f777:#6292ff":55,\
#green (v6):sky-teal-blue
"#50f777:#28d7ff":30,\
#green (v6):purple blue
"#50f777:#9380ff":55,\
#green (v6):teal-blue (v1)
"#50f777:#3bc1f0":30,\
#green (v6):teal-blue (v2)
"#50f777:#34caf0":30,\
#green (v6):teal-blue (v3)
"#50f777:#01b0ed":40,\
#green (v6):gold (v2)
"#50f777:#f9cd48":25,\
#green (v6):gold (v3)
"#50f777:#fed940":25,\
#green (v6):gold (v4)
"#50f777:#ffd700":35,\
#green (v6):orange (v2)
"#50f777:#ffaa5f":30,\
#green (v6):light orange
"#50f777:#ffae7c":30,\
#green (v6):yellow-orange
"#50f777:#ffca5f":20,\
#green (v6):yellow (v1)
"#50f777:#fff03a":15,\
#green (v6):yellow (v2)
"#50f777:#ebdf59":20,\
#green (v6):yellow (v3)
"#50f777:#f1e157":20,\
#green (v6):pink orange
"#50f777:#ff9a84":30,\
#green (v6):indigo (v1)
"#50f777:#c97fff":45,\
#green (v6):indigo (v2)
"#50f777:#6e76ff":65,\

#green (v7):turquoise
"#01f5a1:#01edd2":5,\
#green (v7):medium purple
"#01f5a1:#c66aff":80,\
#green (v7):light electric pink (v1)
"#01f5a1:#eb61ff":75,\
#green (v7):light electric pink (v2)
"#01f5a1:#fc90ff":45,\
#green (v7):electric pink
"#01f5a1:#f574ff":55,\
#green (v7):dark electric pink
"#01f5a1:#ff60e1":45,\
#green (v7):coral
"#01f5a1:#f88379":40,\
#green (v7):purple (v1)
"#01f5a1:#977aff":30,\
#green (v7):purple (v2)
"#01f5a1:#a971fc":25,\
#green (v7):purple (v3)
"#01f5a1:#b76eff":35,\
#green (v7):purple (v4)
"#01f5a1:#d985f7":50,\
#green (v7):purple (v5)
"#01f5a1:#7f5fff":35,\
#green (v7):purple (v6)
"#01f5a1:#a991ff":30,\
#green (v7):purple (v7)
"#01f5a1:#a293ff":50,\
#green (v7):pink (v2)
"#01f5a1:#ff7d9c":60,\
#green (v7):pink (v3)
"#01f5a1:#fc98bc":60,\
#green (v7):reddish (v1)
"#01f5a1:#ff5f5f":40,\
#green (v7):reddish (v2)
"#01f5a1:#ff5a5a":50,\
#green (v7):tomato
"#01f5a1:#ff8282":50,\
#green (v7):greenish yellow
"#01f5a1:#d4d900":30,\
#green (v7):greenish
"#01f5a1:#c8ff28":20,\
#green (v7):aquamarine (v1)
"#01f5a1:#28ffaa":1,\
#green (v7):aquamarine (v2)
"#01f5a1:#00eccb":5,\
#green (v7):firozi (v2)
"#01f5a1:#2ff6ea":5,\
#green (v7):firozi (v3)
"#01f5a1:#49d9ff":15,\
#green (v7):firozi (v4)
"#01f5a1:#31e6ed":7,\
#green (v7):dull green
"#01f5a1:#89e46c":15,\
#green (v7):mint greenish
"#01f5a1:#9de245":10,\
#green (v7):mint green
"#01f5a1:#66ff3a":10,\
#green (v7):light mint green
"#01f5a1:#00f0a9":1,\
#green (v7):light green
"#01f5a1:#a5ed31":15,\
#green (v7):green (v2)
"#01f5a1:#2ff06f":5,\
#green (v7):green (v3)
"#01f5a1:#26e99c":1,\
#green (v7):green (v4)
"#01f5a1:#42ec72":7,\
#green (v7):green (v5)
"#01f5a1:#46ec5c":10,\
#green (v7):green (v6)
"#01f5a1:#50f777":7,\
#green (v7):green (v7)
"#01f5a1:#01f5a1":0,\
#green (v7):green (v8)
"#01f5a1:#42e966":5,\
#green (v7):green (v9)
"#01f5a1:#52f578":1,\
#green (v7):sky blue (v1)
"#01f5a1:#69baf5":40,\
#green (v7):sky blue (v2)
"#01f5a1:#6d9eff":60,\
#green (v7):sky blue (v3)
"#01f5a1:#32a8f8":70,\
#green (v7):sky blue (v4)
"#01f5a1:#5caeff":55,\
#green (v7):sky blue (v5)
"#01f5a1:#7ba6fc":55,\
#green (v7):blue
"#01f5a1:#6292ff":75,\
#green (v7):sky-teal-blue
"#01f5a1:#28d7ff":30,\
#green (v7):purple blue
"#01f5a1:#9380ff":60,\
#green (v7):teal-blue (v1)
"#01f5a1:#3bc1f0":35,\
#green (v7):teal-blue (v2)
"#01f5a1:#34caf0":35,\
#green (v7):teal-blue (v3)
"#01f5a1:#01b0ed":45,\
#green (v7):gold (v2)
"#01f5a1:#f9cd48":40,\
#green (v7):gold (v3)
"#01f5a1:#fed940":40,\
#green (v7):gold (v4)
"#01f5a1:#ffd700":55,\
#green (v7):orange (v2)
"#01f5a1:#ffaa5f":30,\
#green (v7):light orange
"#01f5a1:#ffae7c":25,\
#green (v7):yellow-orange
"#01f5a1:#ffca5f":30,\
#green (v7):yellow (v1)
"#01f5a1:#fff03a":20,\
#green (v7):yellow (v2)
"#01f5a1:#ebdf59":25,\
#green (v7):yellow (v3)
"#01f5a1:#f1e157":25,\
#green (v7):pink orange
"#01f5a1:#ff9a84":35,\
#green (v7):indigo (v1)
"#01f5a1:#c97fff":60,\
#green (v7):indigo (v2)
"#01f5a1:#6e76ff":80,\

#green (v8):turquoise
"#42e966:#01edd2":10,\
#green (v8):medium purple
"#42e966:#c66aff":70,\
#green (v8):light electric pink (v1)
"#42e966:#eb61ff":65,\
#green (v8):light electric pink (v2)
"#42e966:#fc90ff":55,\
#green (v8):electric pink
"#42e966:#f574ff":55,\
#green (v8):dark electric pink
"#42e966:#ff60e1":40,\
#green (v8):coral
"#42e966:#f88379":35,\
#green (v8):purple (v1)
"#42e966:#977aff":35,\
#green (v8):purple (v2)
"#42e966:#a971fc":35,\
#green (v8):purple (v3)
"#42e966:#b76eff":35,\
#green (v8):purple (v4)
"#42e966:#d985f7":55,\
#green (v8):purple (v5)
"#42e966:#7f5fff":35,\
#green (v8):purple (v6)
"#42e966:#a991ff":35,\
#green (v8):purple (v7)
"#42e966:#a293ff":40,\
#green (v8):pink (v2)
"#42e966:#ff7d9c":60,\
#green (v8):pink (v3)
"#42e966:#fc98bc":60,\
#green (v8):reddish (v1)
"#42e966:#ff5f5f":45,\
#green (v8):reddish (v2)
"#42e966:#ff5a5a":50,\
#green (v8):tomato
"#42e966:#ff8282":45,\
#green (v8):greenish yellow
"#42e966:#d4d900":20,\
#green (v8):greenish
"#42e966:#c8ff28":15,\
#green (v8):aquamarine (v1)
"#42e966:#28ffaa":7,\
#green (v8):aquamarine (v2)
"#42e966:#00eccb":10,\
#green (v8):firozi (v2)
"#42e966:#2ff6ea":15,\
#green (v8):firozi (v3)
"#42e966:#49d9ff":20,\
#green (v8):firozi (v4)
"#42e966:#31e6ed":15,\
#green (v8):dull green
"#42e966:#89e46c":7,\
#green (v8):mint greenish
"#42e966:#9de245":10,\
#green (v8):mint green
"#42e966:#66ff3a":7,\
#green (v8):light mint green
"#42e966:#00f0a9":5,\
#green (v8):light green
"#42e966:#a5ed31":10,\
#green (v8):green (v2)
"#42e966:#2ff06f":1,\
#green (v8):green (v3)
"#42e966:#26e99c":5,\
#green (v8):green (v4)
"#42e966:#42ec72":8,\
#green (v8):green (v5)
"#42e966:#46ec5c":1,\
#green (v8):green (v6)
"#42e966:#50f777":1,\
#green (v8):green (v7)
"#42e966:#01f5a1":1,\
#green (v8):green (v8)
"#42e966:#42e966":0,\
#green (v8):green (v9)
"#42e966:#52f578":1,\
#green (v8):sky blue (v1)
"#42e966:#69baf5":40,\
#green (v8):sky blue (v2)
"#42e966:#6d9eff":50,\
#green (v8):sky blue (v3)
"#42e966:#32a8f8":50,\
#green (v8):sky blue (v4)
"#42e966:#5caeff":40,\
#green (v8):sky blue (v5)
"#42e966:#7ba6fc":35,\
#green (v8):blue
"#42e966:#6292ff":55,\
#green (v8):sky-teal-blue
"#42e966:#28d7ff":35,\
#green (v8):purple blue
"#42e966:#9380ff":55,\
#green (v8):teal-blue (v1)
"#42e966:#3bc1f0":30,\
#green (v8):teal-blue (v2)
"#42e966:#34caf0":30,\
#green (v8):teal-blue (v3)
"#42e966:#01b0ed":45,\
#green (v8):gold (v2)
"#42e966:#f9cd48":35,\
#green (v8):gold (v3)
"#42e966:#fed940":30,\
#green (v8):gold (v4)
"#42e966:#ffd700":45,\
#green (v8):orange (v2)
"#42e966:#ffaa5f":35,\
#green (v8):light orange
"#42e966:#ffae7c":30,\
#green (v8):yellow-orange
"#42e966:#ffca5f":25,\
#green (v8):yellow (v1)
"#42e966:#fff03a":15,\
#green (v8):yellow (v2)
"#42e966:#ebdf59":20,\
#green (v8):yellow (v3)
"#42e966:#f1e157":20,\
#green (v8):pink orange
"#42e966:#ff9a84":35,\
#green (v8):indigo (v1)
"#42e966:#c97fff":65,\
#green (v8):indigo (v2)
"#42e966:#6e76ff":70,\

#green (v9):turquoise
"#52f578:#01edd2":10,\
#green (v9):medium purple
"#52f578:#c66aff":55,\
#green (v9):light electric pink (v1)
"#52f578:#eb61ff":50,\
#green (v9):light electric pink (v2)
"#52f578:#fc90ff":40,\
#green (v9):electric pink
"#52f578:#f574ff":40,\
#green (v9):dark electric pink
"#52f578:#ff60e1":25,\
#green (v9):coral
"#52f578:#f88379":25,\
#green (v9):purple (v1)
"#52f578:#977aff":20,\
#green (v9):purple (v2)
"#52f578:#a971fc":30,\
#green (v9):purple (v3)
"#52f578:#b76eff":30,\
#green (v9):purple (v4)
"#52f578:#d985f7":45,\
#green (v9):purple (v5)
"#52f578:#7f5fff":30,\
#green (v9):purple (v6)
"#52f578:#a991ff":25,\
#green (v9):purple (v7)
"#52f578:#a293ff":30,\
#green (v9):pink (v2)
"#52f578:#ff7d9c":50,\
#green (v9):pink (v3)
"#52f578:#fc98bc":50,\
#green (v9):reddish (v1)
"#52f578:#ff5f5f":40,\
#green (v9):reddish (v2)
"#52f578:#ff5a5a":45,\
#green (v9):tomato
"#52f578:#ff8282":40,\
#green (v9):greenish yellow
"#52f578:#d4d900":15,\
#green (v9):greenish
"#52f578:#c8ff28":10,\
#green (v9):aquamarine (v1)
"#52f578:#28ffaa":5,\
#green (v9):aquamarine (v2)
"#52f578:#00eccb":7,\
#green (v9):firozi (v2)
"#52f578:#2ff6ea":10,\
#green (v9):firozi (v3)
"#52f578:#49d9ff":15,\
#green (v9):firozi (v4)
"#52f578:#31e6ed":10,\
#green (v9):dull green
"#52f578:#89e46c":5,\
#green (v9):mint greenish
"#52f578:#9de245":7,\
#green (v9):mint green
"#52f578:#66ff3a":5,\
#green (v9):light mint green
"#52f578:#00f0a9":5,\
#green (v9):light green
"#52f578:#a5ed31":7,\
#green (v9):green (v2)
"#52f578:#2ff06f":1,\
#green (v9):green (v3)
"#52f578:#26e99c":5,\
#green (v9):green (v4)
"#52f578:#42ec72":1,\
#green (v9):green (v5)
"#52f578:#46ec5c":1,\
#green (v9):green (v6)
"#52f578:#50f777":1,\
#green (v9):green (v7)
"#52f578:#01f5a1":1,\
#green (v9):green (v8)
"#52f578:#42e966":1,\
#green (v9):green (v9)
"#52f578:#52f578":0,\
#green (v9):sky blue (v1)
"#52f578:#69baf5":45,\
#green (v9):sky blue (v2)
"#52f578:#6d9eff":55,\
#green (v9):sky blue (v3)
"#52f578:#32a8f8":60,\
#green (v9):sky blue (v4)
"#52f578:#5caeff":40,\
#green (v9):sky blue (v5)
"#52f578:#7ba6fc":35,\
#green (v9):blue
"#52f578:#6292ff":55,\
#green (v9):sky-teal-blue
"#52f578:#28d7ff":35,\
#green (v9):purple blue
"#52f578:#9380ff":60,\
#green (v9):teal-blue (v1)
"#52f578:#3bc1f0":30,\
#green (v9):teal-blue (v2)
"#52f578:#34caf0":30,\
#green (v9):teal-blue (v3)
"#52f578:#01b0ed":55,\
#green (v9):gold (v2)
"#52f578:#f9cd48":25,\
#green (v9):gold (v3)
"#52f578:#fed940":25,\
#green (v9):gold (v4)
"#52f578:#ffd700":35,\
#green (v9):orange (v2)
"#52f578:#ffaa5f":30,\
#green (v9):light orange
"#52f578:#ffae7c":30,\
#green (v9):yellow-orange
"#52f578:#ffca5f":20,\
#green (v9):yellow (v1)
"#52f578:#fff03a":15,\
#green (v9):yellow (v2)
"#52f578:#ebdf59":20,\
#green (v9):yellow (v3)
"#52f578:#f1e157":20,\
#green (v9):pink orange
"#52f578:#ff9a84":35,\
#green (v9):indigo (v1)
"#52f578:#c97fff":45,\
#green (v9):indigo (v2)
"#52f578:#6e76ff":65,\

#sky blue (v1):turquoise
"#69baf5:#01edd2":10,\
#sky blue (v1):medium purple
"#69baf5:#c66aff":20,\
#sky blue (v1):light electric pink (v1)
"#69baf5:#eb61ff":25,\
#sky blue (v1):light electric pink (v2)
"#69baf5:#fc90ff":20,\
#sky blue (v1):electric pink
"#69baf5:#f574ff":25,\
#sky blue (v1):dark electric pink
"#69baf5:#ff60e1":30,\
#sky blue (v1):coral
"#69baf5:#f88379":35,\
#sky blue (v1):purple (v1)
"#69baf5:#977aff":7,\
#sky blue (v1):purple (v2)
"#69baf5:#a971fc":10,\
#sky blue (v1):purple (v3)
"#69baf5:#b76eff":15,\
#sky blue (v1):purple (v4)
"#69baf5:#d985f7":35,\
#sky blue (v1):purple (v5)
"#69baf5:#7f5fff":7,\
#sky blue (v1):purple (v6)
"#69baf5:#a991ff":10,\
#sky blue (v1):purple (v7)
"#69baf5:#a293ff":5,\
#sky blue (v1):pink (v2)
"#69baf5:#ff7d9c":45,\
#sky blue (v1):pink (v3)
"#69baf5:#fc98bc":50,\
#sky blue (v1):reddish (v1)
"#69baf5:#ff5f5f":60,\
#sky blue (v1):reddish (v2)
"#69baf5:#ff5a5a":50,\
#sky blue (v1):tomato
"#69baf5:#ff8282":50,\
#sky blue (v1):greenish yellow
"#69baf5:#d4d900":40,\
#sky blue (v1):greenish
"#69baf5:#c8ff28":35,\
#sky blue (v1):aquamarine (v1)
"#69baf5:#28ffaa":25,\
#sky blue (v1):aquamarine (v2)
"#69baf5:#00eccb":20,\
#sky blue (v1):firozi (v2)
"#69baf5:#2ff6ea":15,\
#sky blue (v1):firozi (v3)
"#69baf5:#49d9ff":5,\
#sky blue (v1):firozi (v4)
"#69baf5:#31e6ed":7,\
#sky blue (v1):dull green
"#69baf5:#89e46c":45,\
#sky blue (v1):mint greenish
"#69baf5:#9de245":40,\
#sky blue (v1):mint green
"#69baf5:#66ff3a":40,\
#sky blue (v1):light mint green
"#69baf5:#00f0a9":25,\
#sky blue (v1):light green
"#69baf5:#a5ed31":30,\
#sky blue (v1):green (v2)
"#69baf5:#2ff06f":25,\
#sky blue (v1):green (v3)
"#69baf5:#26e99c":30,\
#sky blue (v1):green (v4)
"#69baf5:#42ec72":35,\
#sky blue (v1):green (v5)
"#69baf5:#46ec5c":35,\
#sky blue (v1):green (v6)
"#69baf5:#50f777":30,\
#sky blue (v1):green (v7)
"#69baf5:#01f5a1":40,\
#sky blue (v1):green (v8)
"#69baf5:#42e966":40,\
#sky blue (v1):green (v9)
"#69baf5:#52f578":45,\
#sky blue (v1):sky blue (v1)
"#69baf5:#69baf5":0,\
#sky blue (v1):sky blue (v2)
"#69baf5:#6d9eff":1,\
#sky blue (v1):sky blue (v3)
"#69baf5:#32a8f8":1,\
#sky blue (v1):sky blue (v4)
"#69baf5:#5caeff":1,\
#sky blue (v1):sky blue (v5)
"#69baf5:#7ba6fc":1,\
#sky blue (v1):blue
"#69baf5:#6292ff":1,\
#sky blue (v1):sky-teal-blue
"#69baf5:#28d7ff":5,\
#sky blue (v1):purple blue
"#69baf5:#9380ff":10,\
#sky blue (v1):teal-blue (v1)
"#69baf5:#3bc1f0":1,\
#sky blue (v1):teal-blue (v2)
"#69baf5:#34caf0":1,\
#sky blue (v1):teal-blue (v3)
"#69baf5:#01b0ed":5,\
#sky blue (v1):gold (v2)
"#69baf5:#f9cd48":45,\
#sky blue (v1):gold (v3)
"#69baf5:#fed940":45,\
#sky blue (v1):gold (v4)
"#69baf5:#ffd700":60,\
#sky blue (v1):orange (v2)
"#69baf5:#ffaa5f":45,\
#sky blue (v1):light orange
"#69baf5:#ffae7c":40,\
#sky blue (v1):yellow-orange
"#69baf5:#ffca5f":40,\
#sky blue (v1):yellow (v1)
"#69baf5:#fff03a":50,\
#sky blue (v1):yellow (v2)
"#69baf5:#ebdf59":45,\
#sky blue (v1):yellow (v3)
"#69baf5:#f1e157":45,\
#sky blue (v1):pink orange
"#69baf5:#ff9a84":40,\
#sky blue (v1):indigo (v1)
"#69baf5:#c97fff":20,\
#sky blue (v1):indigo (v2)
"#69baf5:#6e76ff":5,\

#sky blue (v2):turquoise
"#6d9eff:#01edd2":15,\
#sky blue (v2):medium purple
"#6d9eff:#c66aff":15,\
#sky blue (v2):light electric pink (v1)
"#6d9eff:#eb61ff":20,\
#sky blue (v2):light electric pink (v2)
"#6d9eff:#fc90ff":25,\
#sky blue (v2):electric pink
"#6d9eff:#f574ff":20,\
#sky blue (v2):dark electric pink
"#6d9eff:#ff60e1":40,\
#sky blue (v2):coral
"#6d9eff:#f88379":40,\
#sky blue (v2):purple (v1)
"#6d9eff:#977aff":5,\
#sky blue (v2):purple (v2)
"#6d9eff:#a971fc":10,\
#sky blue (v2):purple (v3)
"#6d9eff:#b76eff":10,\
#sky blue (v2):purple (v4)
"#6d9eff:#d985f7":40,\
#sky blue (v2):purple (v5)
"#6d9eff:#7f5fff":1,\
#sky blue (v2):purple (v6)
"#6d9eff:#a991ff":10,\
#sky blue (v2):purple (v7)
"#6d9eff:#a293ff":5,\
#sky blue (v2):pink (v2)
"#6d9eff:#ff7d9c":65,\
#sky blue (v2):pink (v3)
"#6d9eff:#fc98bc":55,\
#sky blue (v2):reddish (v1)
"#6d9eff:#ff5f5f":65,\
#sky blue (v2):reddish (v2)
"#6d9eff:#ff5a5a":55,\
#sky blue (v2):tomato
"#6d9eff:#ff8282":55,\
#sky blue (v2):greenish yellow
"#6d9eff:#d4d900":45,\
#sky blue (v2):greenish
"#6d9eff:#c8ff28":40,\
#sky blue (v2):aquamarine (v1)
"#6d9eff:#28ffaa":35,\
#sky blue (v2):aquamarine (v2)
"#6d9eff:#00eccb":30,\
#sky blue (v2):firozi (v2)
"#6d9eff:#2ff6ea":20,\
#sky blue (v2):firozi (v3)
"#6d9eff:#49d9ff":7,\
#sky blue (v2):firozi (v4)
"#6d9eff:#31e6ed":15,\
#sky blue (v2):dull green
"#6d9eff:#89e46c":55,\
#sky blue (v2):mint greenish
"#6d9eff:#9de245":50,\
#sky blue (v2):mint green
"#6d9eff:#66ff3a":50,\
#sky blue (v2):light mint green
"#6d9eff:#00f0a9":35,\
#sky blue (v2):light green
"#6d9eff:#a5ed31":35,\
#sky blue (v2):green (v2)
"#6d9eff:#2ff06f":30,\
#sky blue (v2):green (v3)
"#6d9eff:#26e99c":40,\
#sky blue (v2):green (v4)
"#6d9eff:#42ec72":45,\
#sky blue (v2):green (v5)
"#6d9eff:#46ec5c":45,\
#sky blue (v2):green (v6)
"#6d9eff:#50f777":40,\
#sky blue (v2):green (v7)
"#6d9eff:#01f5a1":60,\
#sky blue (v2):green (v8)
"#6d9eff:#42e966":50,\
#sky blue (v2):green (v9)
"#6d9eff:#52f578":55,\
#sky blue (v2):sky blue (v1)
"#6d9eff:#69baf5":1,\
#sky blue (v2):sky blue (v2)
"#6d9eff:#6d9eff":0,\
#sky blue (v2):sky blue (v3)
"#6d9eff:#32a8f8":1,\
#sky blue (v2):sky blue (v4)
"#6d9eff:#5caeff":1,\
#sky blue (v2):sky blue (v5)
"#6d9eff:#7ba6fc":1,\
#sky blue (v2):blue
"#6d9eff:#6292ff":1,\
#sky blue (v2):sky-teal-blue
"#6d9eff:#28d7ff":10,\
#sky blue (v2):purple blue
"#6d9eff:#9380ff":7,\
#sky blue (v2):teal-blue (v1)
"#6d9eff:#3bc1f0":5,\
#sky blue (v2):teal-blue (v2)
"#6d9eff:#34caf0":5,\
#sky blue (v2):teal-blue (v3)
"#6d9eff:#01b0ed":5,\
#sky blue (v2):gold (v2)
"#6d9eff:#f9cd48":45,\
#sky blue (v2):gold (v3)
"#6d9eff:#fed940":45,\
#sky blue (v2):gold (v4)
"#6d9eff:#ffd700":60,\
#sky blue (v2):orange (v2)
"#6d9eff:#ffaa5f":25,\
#sky blue (v2):light orange
"#6d9eff:#ffae7c":25,\
#sky blue (v2):yellow-orange
"#6d9eff:#ffca5f":40,\
#sky blue (v2):yellow (v1)
"#6d9eff:#fff03a":65,\
#sky blue (v2):yellow (v2)
"#6d9eff:#ebdf59":55,\
#sky blue (v2):yellow (v3)
"#6d9eff:#f1e157":55,\
#sky blue (v2):pink orange
"#6d9eff:#ff9a84":35,\
#sky blue (v2):indigo (v1)
"#6d9eff:#c97fff":15,\
#sky blue (v2):indigo (v2)
"#6d9eff:#6e76ff":5,\

#sky blue (v3):turquoise
"#32a8f8:#01edd2":25,\
#sky blue (v3):medium purple
"#32a8f8:#c66aff":20,\
#sky blue (v3):light electric pink (v1)
"#32a8f8:#eb61ff":35,\
#sky blue (v3):light electric pink (v2)
"#32a8f8:#fc90ff":35,\
#sky blue (v3):electric pink
"#32a8f8:#f574ff":30,\
#sky blue (v3):dark electric pink
"#32a8f8:#ff60e1":50,\
#sky blue (v3):coral
"#32a8f8:#f88379":55,\
#sky blue (v3):purple (v1)
"#32a8f8:#977aff":10,\
#sky blue (v3):purple (v2)
"#32a8f8:#a971fc":10,\
#sky blue (v3):purple (v3)
"#32a8f8:#b76eff":20,\
#sky blue (v3):purple (v4)
"#32a8f8:#d985f7":45,\
#sky blue (v3):purple (v5)
"#32a8f8:#7f5fff":5,\
#sky blue (v3):purple (v6)
"#32a8f8:#a991ff":15,\
#sky blue (v3):purple (v7)
"#32a8f8:#a293ff":15,\
#sky blue (v3):pink (v2)
"#32a8f8:#ff7d9c":70,\
#sky blue (v3):pink (v3)
"#32a8f8:#fc98bc":60,\
#sky blue (v3):reddish (v1)
"#32a8f8:#ff5f5f":70,\
#sky blue (v3):reddish (v2)
"#32a8f8:#ff5a5a":60,\
#sky blue (v3):tomato
"#32a8f8:#ff8282":60,\
#sky blue (v3):greenish yellow
"#32a8f8:#d4d900":55,\
#sky blue (v3):greenish
"#32a8f8:#c8ff28":50,\
#sky blue (v3):aquamarine (v1)
"#32a8f8:#28ffaa":40,\
#sky blue (v3):aquamarine (v2)
"#32a8f8:#00eccb":30,\
#sky blue (v3):firozi (v2)
"#32a8f8:#2ff6ea":20,\
#sky blue (v3):firozi (v3)
"#32a8f8:#49d9ff":5,\
#sky blue (v3):firozi (v4)
"#32a8f8:#31e6ed":15,\
#sky blue (v3):dull green
"#32a8f8:#89e46c":60,\
#sky blue (v3):mint greenish
"#32a8f8:#9de245":55,\
#sky blue (v3):mint green
"#32a8f8:#66ff3a":60,\
#sky blue (v3):light mint green
"#32a8f8:#00f0a9":35,\
#sky blue (v3):light green
"#32a8f8:#a5ed31":45,\
#sky blue (v3):green (v2)
"#32a8f8:#2ff06f":45,\
#sky blue (v3):green (v3)
"#32a8f8:#26e99c":45,\
#sky blue (v3):green (v4)
"#32a8f8:#42ec72":50,\
#sky blue (v3):green (v5)
"#32a8f8:#46ec5c":50,\
#sky blue (v3):green (v6)
"#32a8f8:#50f777":50,\
#sky blue (v3):green (v7)
"#32a8f8:#01f5a1":45,\
#sky blue (v3):green (v8)
"#32a8f8:#42e966":70,\
#sky blue (v3):green (v9)
"#32a8f8:#52f578":50,\
#sky blue (v3):sky blue (v1)
"#32a8f8:#69baf5":60,\
#sky blue (v3):sky blue (v2)
"#32a8f8:#6d9eff":1,\
#sky blue (v3):sky blue (v3)
"#32a8f8:#32a8f8":0,\
#sky blue (v3):sky blue (v4)
"#32a8f8:#5caeff":5,\
#sky blue (v3):sky blue (v5)
"#32a8f8:#7ba6fc":5,\
#sky blue (v3):blue
"#32a8f8:#6292ff":1,\
#sky blue (v3):sky-teal-blue
"#32a8f8:#28d7ff":10,\
#sky blue (v3):purple blue
"#32a8f8:#9380ff":10,\
#sky blue (v3):teal-blue (v1)
"#32a8f8:#3bc1f0":7,\
#sky blue (v3):teal-blue (v2)
"#32a8f8:#34caf0":7,\
#sky blue (v3):teal-blue (v3)
"#32a8f8:#01b0ed":1,\
#sky blue (v3):gold (v2)
"#32a8f8:#f9cd48":45,\
#sky blue (v3):gold (v3)
"#32a8f8:#fed940":45,\
#sky blue (v3):gold (v4)
"#32a8f8:#ffd700":65,\
#sky blue (v3):orange (v2)
"#32a8f8:#ffaa5f":35,\
#sky blue (v3):light orange
"#32a8f8:#ffae7c":30,\
#sky blue (v3):yellow-orange
"#32a8f8:#ffca5f":40,\
#sky blue (v3):yellow (v1)
"#32a8f8:#fff03a":60,\
#sky blue (v3):yellow (v2)
"#32a8f8:#ebdf59":40,\
#sky blue (v3):yellow (v3)
"#32a8f8:#f1e157":40,\
#sky blue (v3):pink orange
"#32a8f8:#ff9a84":35,\
#sky blue (v3):indigo (v1)
"#32a8f8:#c97fff":15,\
#sky blue (v3):indigo (v2)
"#32a8f8:#6e76ff":5,\

#sky blue (v4):turquoise
"#5caeff:#01edd2":15,\
#sky blue (v4):medium purple
"#5caeff:#c66aff":20,\
#sky blue (v4):light electric pink (v1)
"#5caeff:#eb61ff":20,\
#sky blue (v4):light electric pink (v2)
"#5caeff:#fc90ff":25,\
#sky blue (v4):electric pink
"#5caeff:#f574ff":20,\
#sky blue (v4):dark electric pink
"#5caeff:#ff60e1":40,\
#sky blue (v4):coral
"#5caeff:#f88379":40,\
#sky blue (v4):purple (v1)
"#5caeff:#977aff":7,\
#sky blue (v4):purple (v2)
"#5caeff:#a971fc":7,\
#sky blue (v4):purple (v3)
"#5caeff:#b76eff":15,\
#sky blue (v4):purple (v4)
"#5caeff:#d985f7":40,\
#sky blue (v4):purple (v5)
"#5caeff:#7f5fff":7,\
#sky blue (v4):purple (v6)
"#5caeff:#a991ff":10,\
#sky blue (v4):purple (v7)
"#5caeff:#a293ff":5,\
#sky blue (v4):pink (v2)
"#5caeff:#ff7d9c":60,\
#sky blue (v4):pink (v3)
"#5caeff:#fc98bc":50,\
#sky blue (v4):reddish (v1)
"#5caeff:#ff5f5f":60,\
#sky blue (v4):reddish (v2)
"#5caeff:#ff5a5a":55,\
#sky blue (v4):tomato
"#5caeff:#ff8282":50,\
#sky blue (v4):greenish yellow
"#5caeff:#d4d900":45,\
#sky blue (v4):greenish
"#5caeff:#c8ff28":35,\
#sky blue (v4):aquamarine (v1)
"#5caeff:#28ffaa":35,\
#sky blue (v4):aquamarine (v2)
"#5caeff:#00eccb":25,\
#sky blue (v4):firozi (v2)
"#5caeff:#2ff6ea":15,\
#sky blue (v4):firozi (v3)
"#5caeff:#49d9ff":5,\
#sky blue (v4):firozi (v4)
"#5caeff:#31e6ed":7,\
#sky blue (v4):dull green
"#5caeff:#89e46c":45,\
#sky blue (v4):mint greenish
"#5caeff:#9de245":40,\
#sky blue (v4):mint green
"#5caeff:#66ff3a":50,\
#sky blue (v4):light mint green
"#5caeff:#00f0a9":30,\
#sky blue (v4):light green
"#5caeff:#a5ed31":40,\
#sky blue (v4):green (v2)
"#5caeff:#2ff06f":25,\
#sky blue (v4):green (v3)
"#5caeff:#26e99c":40,\
#sky blue (v4):green (v4)
"#5caeff:#42ec72":40,\
#sky blue (v4):green (v5)
"#5caeff:#46ec5c":40,\
#sky blue (v4):green (v6)
"#5caeff:#50f777":40,\
#sky blue (v4):green (v7)
"#5caeff:#01f5a1":55,\
#sky blue (v4):green (v8)
"#5caeff:#42e966":40,\
#sky blue (v4):green (v9)
"#5caeff:#52f578":40,\
#sky blue (v4):sky blue (v1)
"#5caeff:#69baf5":1,\
#sky blue (v4):sky blue (v2)
"#5caeff:#6d9eff":1,\
#sky blue (v4):sky blue (v3)
"#5caeff:#32a8f8":5,\
#sky blue (v4):sky blue (v4)
"#5caeff:#5caeff":0,\
#sky blue (v4):sky blue (v5)
"#5caeff:#7ba6fc":5,\
#sky blue (v4):blue
"#5caeff:#6292ff":1,\
#sky blue (v4):sky-teal-blue
"#5caeff:#28d7ff":10,\
#sky blue (v4):purple blue
"#5caeff:#9380ff":7,\
#sky blue (v4):teal-blue (v1)
"#5caeff:#3bc1f0":7,\
#sky blue (v4):teal-blue (v2)
"#5caeff:#34caf0":7,\
#sky blue (v4):teal-blue (v3)
"#5caeff:#01b0ed":5,\
#sky blue (v4):gold (v2)
"#5caeff:#f9cd48":45,\
#sky blue (v4):gold (v3)
"#5caeff:#fed940":50,\
#sky blue (v4):gold (v4)
"#5caeff:#ffd700":65,\
#sky blue (v4):orange (v2)
"#5caeff:#ffaa5f":45,\
#sky blue (v4):light orange
"#5caeff:#ffae7c":40,\
#sky blue (v4):yellow-orange
"#5caeff:#ffca5f":30,\
#sky blue (v4):yellow (v1)
"#5caeff:#fff03a":40,\
#sky blue (v4):yellow (v2)
"#5caeff:#ebdf59":25,\
#sky blue (v4):yellow (v3)
"#5caeff:#f1e157":25,\
#sky blue (v4):pink orange
"#5caeff:#ff9a84":35,\
#sky blue (v4):indigo (v1)
"#5caeff:#c97fff":15,\
#sky blue (v4):indigo (v2)
"#5caeff:#6e76ff":7,\

#sky blue (v5):turquoise
"#7ba6fc:#01edd2":15,\
#sky blue (v5):medium purple
"#7ba6fc:#c66aff":15,\
#sky blue (v5):light electric pink (v1)
"#7ba6fc:#eb61ff":15,\
#sky blue (v5):light electric pink (v2)
"#7ba6fc:#fc90ff":15,\
#sky blue (v5):electric pink
"#7ba6fc:#f574ff":15,\
#sky blue (v5):dark electric pink
"#7ba6fc:#ff60e1":25,\
#sky blue (v5):coral
"#7ba6fc:#f88379":35,\
#sky blue (v5):purple (v1)
"#7ba6fc:#977aff":5,\
#sky blue (v5):purple (v2)
"#7ba6fc:#a971fc":5,\
#sky blue (v5):purple (v3)
"#7ba6fc:#b76eff":10,\
#sky blue (v5):purple (v4)
"#7ba6fc:#d985f7":30,\
#sky blue (v5):purple (v5)
"#7ba6fc:#7f5fff":5,\
#sky blue (v5):purple (v6)
"#7ba6fc:#a991ff":5,\
#sky blue (v5):purple (v7)
"#7ba6fc:#a293ff":1,\
#sky blue (v5):pink (v2)
"#7ba6fc:#ff7d9c":50,\
#sky blue (v5):pink (v3)
"#7ba6fc:#fc98bc":45,\
#sky blue (v5):reddish (v1)
"#7ba6fc:#ff5f5f":50,\
#sky blue (v5):reddish (v2)
"#7ba6fc:#ff5a5a":50,\
#sky blue (v5):tomato
"#7ba6fc:#ff8282":40,\
#sky blue (v5):greenish yellow
"#7ba6fc:#d4d900":45,\
#sky blue (v5):greenish
"#7ba6fc:#c8ff28":35,\
#sky blue (v5):aquamarine (v1)
"#7ba6fc:#28ffaa":35,\
#sky blue (v5):aquamarine (v2)
"#7ba6fc:#00eccb":25,\
#sky blue (v5):firozi (v2)
"#7ba6fc:#2ff6ea":15,\
#sky blue (v5):firozi (v3)
"#7ba6fc:#49d9ff":5,\
#sky blue (v5):firozi (v4)
"#7ba6fc:#31e6ed":7,\
#sky blue (v5):dull green
"#7ba6fc:#89e46c":45,\
#sky blue (v5):mint greenish
"#7ba6fc:#9de245":40,\
#sky blue (v5):mint green
"#7ba6fc:#66ff3a":50,\
#sky blue (v5):light mint green
"#7ba6fc:#00f0a9":30,\
#sky blue (v5):light green
"#7ba6fc:#a5ed31":35,\
#sky blue (v5):green (v2)
"#7ba6fc:#2ff06f":25,\
#sky blue (v5):green (v3)
"#7ba6fc:#26e99c":40,\
#sky blue (v5):green (v4)
"#7ba6fc:#42ec72":40,\
#sky blue (v5):green (v5)
"#7ba6fc:#46ec5c":40,\
#sky blue (v5):green (v6)
"#7ba6fc:#50f777":40,\
#sky blue (v5):green (v7)
"#7ba6fc:#01f5a1":55,\
#sky blue (v5):green (v8)
"#7ba6fc:#42e966":35,\
#sky blue (v5):green (v9)
"#7ba6fc:#52f578":35,\
#sky blue (v5):sky blue (v1)
"#7ba6fc:#69baf5":1,\
#sky blue (v5):sky blue (v2)
"#7ba6fc:#6d9eff":1,\
#sky blue (v5):sky blue (v3)
"#7ba6fc:#32a8f8":5,\
#sky blue (v5):sky blue (v4)
"#7ba6fc:#5caeff":5,\
#sky blue (v5):sky blue (v5)
"#7ba6fc:#7ba6fc":0,\
#sky blue (v5):blue
"#7ba6fc:#6292ff":1,\
#sky blue (v5):sky-teal-blue
"#7ba6fc:#28d7ff":10,\
#sky blue (v5):purple blue
"#7ba6fc:#9380ff":7,\
#sky blue (v5):teal-blue (v1)
"#7ba6fc:#3bc1f0":10,\
#sky blue (v5):teal-blue (v2)
"#7ba6fc:#34caf0":10,\
#sky blue (v5):teal-blue (v3)
"#7ba6fc:#01b0ed":5,\
#sky blue (v5):gold (v2)
"#7ba6fc:#f9cd48":45,\
#sky blue (v5):gold (v3)
"#7ba6fc:#fed940":45,\
#sky blue (v5):gold (v4)
"#7ba6fc:#ffd700":70,\
#sky blue (v5):orange (v2)
"#7ba6fc:#ffaa5f":35,\
#sky blue (v5):light orange
"#7ba6fc:#ffae7c":30,\
#sky blue (v5):yellow-orange
"#7ba6fc:#ffca5f":40,\
#sky blue (v5):yellow (v1)
"#7ba6fc:#fff03a":55,\
#sky blue (v5):yellow (v2)
"#7ba6fc:#ebdf59":35,\
#sky blue (v5):yellow (v3)
"#7ba6fc:#f1e157":35,\
#sky blue (v5):pink orange
"#7ba6fc:#ff9a84":40,\
#sky blue (v5):indigo (v1)
"#7ba6fc:#c97fff":20,\
#sky blue (v5):indigo (v2)
"#7ba6fc:#6e76ff":5,\

#blue:turquoise
"#6292ff:#01edd2":20,\
#blue:medium purple
"#6292ff:#c66aff":15,\
#blue:light electric pink (v1)
"#6292ff:#eb61ff":25,\
#blue:light electric pink (v2)
"#6292ff:#fc90ff":20,\
#blue:electric pink
"#6292ff:#f574ff":30,\
#blue:dark electric pink
"#6292ff:#ff60e1":35,\
#blue:coral
"#6292ff:#f88379":45,\
#blue:purple (v1)
"#6292ff:#977aff":5,\
#blue:purple (v2)
"#6292ff:#a971fc":7,\
#blue:purple (v3)
"#6292ff:#b76eff":10,\
#blue:purple (v4)
"#6292ff:#d985f7":40,\
#blue:purple (v5)
"#6292ff:#7f5fff":1,\
#blue:purple (v6)
"#6292ff:#a991ff":7,\
#blue:purple (v7)
"#6292ff:#a293ff":7,\
#blue:pink (v2)
"#6292ff:#ff7d9c":65,\
#blue:pink (v3)
"#6292ff:#fc98bc":55,\
#blue:reddish (v1)
"#6292ff:#ff5f5f":70,\
#blue:reddish (v2)
"#6292ff:#ff5a5a":60,\
#blue:tomato
"#6292ff:#ff8282":70,\
#blue:greenish yellow
"#6292ff:#d4d900":55,\
#blue:greenish
"#6292ff:#c8ff28":65,\
#blue:aquamarine (v1)
"#6292ff:#28ffaa":40,\
#blue:aquamarine (v2)
"#6292ff:#00eccb":40,\
#blue:firozi (v2)
"#6292ff:#2ff6ea":30,\
#blue:firozi (v3)
"#6292ff:#49d9ff":7,\
#blue:firozi (v4)
"#6292ff:#31e6ed":20,\
#blue:dull green
"#6292ff:#89e46c":55,\
#blue:mint greenish
"#6292ff:#9de245":50,\
#blue:mint green
"#6292ff:#66ff3a":70,\
#blue:light mint green
"#6292ff:#00f0a9":50,\
#blue:light green
"#6292ff:#a5ed31":55,\
#blue:green (v2)
"#6292ff:#2ff06f":45,\
#blue:green (v3)
"#6292ff:#26e99c":50,\
#blue:green (v4)
"#6292ff:#42ec72":60,\
#blue:green (v5)
"#6292ff:#46ec5c":55,\
#blue:green (v6)
"#6292ff:#50f777":55,\
#blue:green (v7)
"#6292ff:#01f5a1":75,\
#blue:green (v8)
"#6292ff:#42e966":55,\
#blue:green (v9)
"#6292ff:#52f578":55,\
#blue:sky blue (v1)
"#6292ff:#69baf5":1,\
#blue:sky blue (v2)
"#6292ff:#6d9eff":1,\
#blue:sky blue (v3)
"#6292ff:#32a8f8":1,\
#blue:sky blue (v4)
"#6292ff:#5caeff":1,\
#blue:sky blue (v5)
"#6292ff:#7ba6fc":1,\
#blue:blue
"#6292ff:#6292ff":0,\
#blue:sky-teal-blue
"#6292ff:#28d7ff":10,\
#blue:purple blue
"#6292ff:#9380ff":7,\
#blue:teal-blue (v1)
"#6292ff:#3bc1f0":10,\
#blue:teal-blue (v2)
"#6292ff:#34caf0":7,\
#blue:teal-blue (v3)
"#6292ff:#01b0ed":5,\
#blue:gold (v2)
"#6292ff:#f9cd48":50,\
#blue:gold (v3)
"#6292ff:#fed940":60,\
#blue:gold (v4)
"#6292ff:#ffd700":75,\
#blue:orange (v2)
"#6292ff:#ffaa5f":40,\
#blue:light orange
"#6292ff:#ffae7c":40,\
#blue:yellow-orange
"#6292ff:#ffca5f":45,\
#blue:yellow (v1)
"#6292ff:#fff03a":55,\
#blue:yellow (v2)
"#6292ff:#ebdf59":45,\
#blue:yellow (v3)
"#6292ff:#f1e157":45,\
#blue:pink orange
"#6292ff:#ff9a84":40,\
#blue:indigo (v1)
"#6292ff:#c97fff":20,\
#blue:indigo (v2)
"#6292ff:#6e76ff":5,\

#sky-teal-blue:turquoise
"#28d7ff:#01edd2":7,\
#sky-teal-blue:medium purple
"#28d7ff:#c66aff":25,\
#sky-teal-blue:light electric pink (v1)
"#28d7ff:#eb61ff":35,\
#sky-teal-blue:light electric pink (v2)
"#28d7ff:#fc90ff":30,\
#sky-teal-blue:electric pink
"#28d7ff:#f574ff":75,\
#sky-teal-blue:dark electric pink
"#28d7ff:#ff60e1":55,\
#sky-teal-blue:coral
"#28d7ff:#f88379":55,\
#sky-teal-blue:purple (v1)
"#28d7ff:#977aff":15,\
#sky-teal-blue:purple (v2)
"#28d7ff:#a971fc":15,\
#sky-teal-blue:purple (v3)
"#28d7ff:#b76eff":15,\
#sky-teal-blue:purple (v4)
"#28d7ff:#d985f7":45,\
#sky-teal-blue:purple (v5)
"#28d7ff:#7f5fff":15,\
#sky-teal-blue:purple (v6)
"#28d7ff:#a991ff":15,\
#sky-teal-blue:purple (v7)
"#28d7ff:#a293ff":15,\
#sky-teal-blue:pink (v2)
"#28d7ff:#ff7d9c":40,\
#sky-teal-blue:pink (v3)
"#28d7ff:#fc98bc":40,\
#sky-teal-blue:reddish (v1)
"#28d7ff:#ff5f5f":70,\
#sky-teal-blue:reddish (v2)
"#28d7ff:#ff5a5a":45,\
#sky-teal-blue:tomato
"#28d7ff:#ff8282":45,\
#sky-teal-blue:greenish yellow
"#28d7ff:#d4d900":40,\
#sky-teal-blue:greenish
"#28d7ff:#c8ff28":35,\
#sky-teal-blue:aquamarine (v1)
"#28d7ff:#28ffaa":20,\
#sky-teal-blue:aquamarine (v2)
"#28d7ff:#00eccb":10,\
#sky-teal-blue:firozi (v2)
"#28d7ff:#2ff6ea":5,\
#sky-teal-blue:firozi (v3)
"#28d7ff:#49d9ff":5,\
#sky-teal-blue:firozi (v4)
"#28d7ff:#31e6ed":1,\
#sky-teal-blue:dull green
"#28d7ff:#89e46c":30,\
#sky-teal-blue:mint greenish
"#28d7ff:#9de245":35,\
#sky-teal-blue:mint green
"#28d7ff:#66ff3a":35,\
#sky-teal-blue:light mint green
"#28d7ff:#00f0a9":15,\
#sky-teal-blue:light green
"#28d7ff:#a5ed31":35,\
#sky-teal-blue:green (v2)
"#28d7ff:#2ff06f":30,\
#sky-teal-blue:green (v3)
"#28d7ff:#26e99c":30,\
#sky-teal-blue:green (v4)
"#28d7ff:#42ec72":35,\
#sky-teal-blue:green (v5)
"#28d7ff:#46ec5c":30,\
#sky-teal-blue:green (v6)
"#28d7ff:#50f777":30,\
#sky-teal-blue:green (v7)
"#28d7ff:#01f5a1":30,\
#sky-teal-blue:green (v8)
"#28d7ff:#42e966":35,\
#sky-teal-blue:green (v9)
"#28d7ff:#52f578":35,\
#sky-teal-blue:sky blue (v1)
"#28d7ff:#69baf5":5,\
#sky-teal-blue:sky blue (v2)
"#28d7ff:#6d9eff":10,\
#sky-teal-blue:sky blue (v3)
"#28d7ff:#32a8f8":10,\
#sky-teal-blue:sky blue (v4)
"#28d7ff:#5caeff":10,\
#sky-teal-blue:sky blue (v5)
"#28d7ff:#7ba6fc":10,\
#sky-teal-blue:blue
"#28d7ff:#6292ff":10,\
#sky-teal-blue:sky-teal-blue
"#28d7ff:#28d7ff":0,\
#sky-teal-blue:purple blue
"#28d7ff:#9380ff":15,\
#sky-teal-blue:teal-blue (v1)
"#28d7ff:#3bc1f0":1,\
#sky-teal-blue:teal-blue (v2)
"#28d7ff:#34caf0":1,\
#sky-teal-blue:teal-blue (v3)
"#28d7ff:#01b0ed":5,\
#sky-teal-blue:gold (v2)
"#28d7ff:#f9cd48":35,\
#sky-teal-blue:gold (v3)
"#28d7ff:#fed940":40,\
#sky-teal-blue:gold (v4)
"#28d7ff:#ffd700":65,\
#sky-teal-blue:orange (v2)
"#28d7ff:#ffaa5f":40,\
#sky-teal-blue:light orange
"#28d7ff:#ffae7c":40,\
#sky-teal-blue:yellow-orange
"#28d7ff:#ffca5f":45,\
#sky-teal-blue:yellow (v1)
"#28d7ff:#fff03a":55,\
#sky-teal-blue:yellow (v2)
"#28d7ff:#ebdf59":45,\
#sky-teal-blue:yellow (v3)
"#28d7ff:#f1e157":45,\
#sky-teal-blue:pink orange
"#28d7ff:#ff9a84":40,\
#sky-teal-blue:indigo (v1)
"#28d7ff:#c97fff":20,\
#sky-teal-blue:indigo (v2)
"#28d7ff:#6e76ff":10,\

#purple blue:turquoise
"#9380ff:#01edd2":35,\
#purple blue:medium purple
"#9380ff:#c66aff":5,\
#purple blue:light electric pink (v1)
"#9380ff:#eb61ff":10,\
#purple blue:light electric pink (v2)
"#9380ff:#fc90ff":10,\
#purple blue:electric pink
"#9380ff:#f574ff":10,\
#purple blue:dark electric pink
"#9380ff:#ff60e1":15,\
#purple blue:coral
"#9380ff:#f88379":30,\
#purple blue:purple (v1)
"#9380ff:#977aff":1,\
#purple blue:purple (v2)
"#9380ff:#a971fc":1,\
#purple blue:purple (v3)
"#9380ff:#b76eff":1,\
#purple blue:purple (v4)
"#9380ff:#d985f7":15,\
#purple blue:purple (v5)
"#9380ff:#7f5fff":5,\
#purple blue:purple (v6)
"#9380ff:#a991ff":1,\
#purple blue:purple (v7)
"#9380ff:#a293ff":1,\
#purple blue:pink (v2)
"#9380ff:#ff7d9c":30,\
#purple blue:pink (v3)
"#9380ff:#fc98bc":45,\
#purple blue:reddish (v1)
"#9380ff:#ff5f5f":35,\
#purple blue:reddish (v2)
"#9380ff:#ff5a5a":40,\
#purple blue:tomato
"#9380ff:#ff8282":40,\
#purple blue:greenish yellow
"#9380ff:#d4d900":60,\
#purple blue:greenish
"#9380ff:#c8ff28":45,\
#purple blue:aquamarine (v1)
"#9380ff:#28ffaa":30,\
#purple blue:aquamarine (v2)
"#9380ff:#00eccb":45,\
#purple blue:firozi (v2)
"#9380ff:#2ff6ea":40,\
#purple blue:firozi (v3)
"#9380ff:#49d9ff":15,\
#purple blue:firozi (v4)
"#9380ff:#31e6ed":25,\
#purple blue:dull green
"#9380ff:#89e46c":60,\
#purple blue:mint greenish
"#9380ff:#9de245":45,\
#purple blue:mint green
"#9380ff:#66ff3a":70,\
#purple blue:light mint green
"#9380ff:#00f0a9":35,\
#purple blue:light green
"#9380ff:#a5ed31":55,\
#purple blue:green (v2)
"#9380ff:#2ff06f":45,\
#purple blue:green (v3)
"#9380ff:#26e99c":45,\
#purple blue:green (v4)
"#9380ff:#42ec72":50,\
#purple blue:green (v5)
"#9380ff:#46ec5c":55,\
#purple blue:green (v6)
"#9380ff:#50f777":55,\
#purple blue:green (v7)
"#9380ff:#01f5a1":60,\
#purple blue:green (v8)
"#9380ff:#42e966":55,\
#purple blue:green (v9)
"#9380ff:#52f578":60,\
#purple blue:sky blue (v1)
"#9380ff:#69baf5":10,\
#purple blue:sky blue (v2)
"#9380ff:#6d9eff":7,\
#purple blue:sky blue (v3)
"#9380ff:#32a8f8":10,\
#purple blue:sky blue (v4)
"#9380ff:#5caeff":7,\
#purple blue:sky blue (v5)
"#9380ff:#7ba6fc":7,\
#purple blue:blue
"#9380ff:#6292ff":7,\
#purple blue:sky-teal-blue
"#9380ff:#28d7ff":15,\
#purple blue:purple blue
"#9380ff:#9380ff":0,\
#purple blue:teal-blue (v1)
"#9380ff:#3bc1f0":15,\
#purple blue:teal-blue (v2)
"#9380ff:#34caf0":15,\
#purple blue:teal-blue (v3)
"#9380ff:#01b0ed":10,\
#purple blue:gold (v2)
"#9380ff:#f9cd48":50,\
#purple blue:gold (v3)
"#9380ff:#fed940":50,\
#purple blue:gold (v4)
"#9380ff:#ffd700":70,\
#purple blue:orange (v2)
"#9380ff:#ffaa5f":45,\
#purple blue:light orange
"#9380ff:#ffae7c":40,\
#purple blue:yellow-orange
"#9380ff:#ffca5f":30,\
#purple blue:yellow (v1)
"#9380ff:#fff03a":70,\
#purple blue:yellow (v2)
"#9380ff:#ebdf59":60,\
#purple blue:yellow (v3)
"#9380ff:#f1e157":60,\
#purple blue:pink orange
"#9380ff:#ff9a84":30,\
#purple blue:indigo (v1)
"#9380ff:#c97fff":10,\
#purple blue:indigo (v2)
"#9380ff:#6e76ff":1,\

#teal-blue (v1):turquoise
"#3bc1f0:#01edd2":7,\
#teal-blue (v1):medium purple
"#3bc1f0:#c66aff":20,\
#teal-blue (v1):light electric pink (v1)
"#3bc1f0:#eb61ff":25,\
#teal-blue (v1):light electric pink (v2)
"#3bc1f0:#fc90ff":20,\
#teal-blue (v1):electric pink
"#3bc1f0:#f574ff":40,\
#teal-blue (v1):dark electric pink
"#3bc1f0:#ff60e1":35,\
#teal-blue (v1):coral
"#3bc1f0:#f88379":40,\
#teal-blue (v1):purple (v1)
"#3bc1f0:#977aff":15,\
#teal-blue (v1):purple (v2)
"#3bc1f0:#a971fc":15,\
#teal-blue (v1):purple (v3)
"#3bc1f0:#b76eff":20,\
#teal-blue (v1):purple (v4)
"#3bc1f0:#d985f7":25,\
#teal-blue (v1):purple (v5)
"#3bc1f0:#7f5fff":15,\
#teal-blue (v1):purple (v6)
"#3bc1f0:#a991ff":15,\
#teal-blue (v1):purple (v7)
"#3bc1f0:#a293ff":15,\
#teal-blue (v1):pink (v2)
"#3bc1f0:#ff7d9c":30,\
#teal-blue (v1):pink (v3)
"#3bc1f0:#fc98bc":40,\
#teal-blue (v1):reddish (v1)
"#3bc1f0:#ff5f5f":30,\
#teal-blue (v1):reddish (v2)
"#3bc1f0:#ff5a5a":40,\
#teal-blue (v1):tomato
"#3bc1f0:#ff8282":40,\
#teal-blue (v1):greenish yellow
"#3bc1f0:#d4d900":45,\
#teal-blue (v1):greenish
"#3bc1f0:#c8ff28":35,\
#teal-blue (v1):aquamarine (v1)
"#3bc1f0:#28ffaa":20,\
#teal-blue (v1):aquamarine (v2)
"#3bc1f0:#00eccb":10,\
#teal-blue (v1):firozi (v2)
"#3bc1f0:#2ff6ea":5,\
#teal-blue (v1):firozi (v3)
"#3bc1f0:#49d9ff":1,\
#teal-blue (v1):firozi (v4)
"#3bc1f0:#31e6ed":1,\
#teal-blue (v1):dull green
"#3bc1f0:#89e46c":30,\
#teal-blue (v1):mint greenish
"#3bc1f0:#9de245":50,\
#teal-blue (v1):mint green
"#3bc1f0:#66ff3a":40,\
#teal-blue (v1):light mint green
"#3bc1f0:#00f0a9":20,\
#teal-blue (v1):light green
"#3bc1f0:#a5ed31":40,\
#teal-blue (v1):green (v2)
"#3bc1f0:#2ff06f":30,\
#teal-blue (v1):green (v3)
"#3bc1f0:#26e99c":35,\
#teal-blue (v1):green (v4)
"#3bc1f0:#42ec72":30,\
#teal-blue (v1):green (v5)
"#3bc1f0:#46ec5c":35,\
#teal-blue (v1):green (v6)
"#3bc1f0:#50f777":30,\
#teal-blue (v1):green (v7)
"#3bc1f0:#01f5a1":35,\
#teal-blue (v1):green (v8)
"#3bc1f0:#42e966":30,\
#teal-blue (v1):green (v9)
"#3bc1f0:#52f578":30,\
#teal-blue (v1):sky blue (v1)
"#3bc1f0:#69baf5":1,\
#teal-blue (v1):sky blue (v2)
"#3bc1f0:#6d9eff":5,\
#teal-blue (v1):sky blue (v3)
"#3bc1f0:#32a8f8":7,\
#teal-blue (v1):sky blue (v4)
"#3bc1f0:#5caeff":7,\
#teal-blue (v1):sky blue (v5)
"#3bc1f0:#7ba6fc":10,\
#teal-blue (v1):blue
"#3bc1f0:#6292ff":10,\
#teal-blue (v1):sky-teal-blue
"#3bc1f0:#28d7ff":1,\
#teal-blue (v1):purple blue
"#3bc1f0:#9380ff":15,\
#teal-blue (v1):teal-blue (v1)
"#3bc1f0:#3bc1f0":0,\
#teal-blue (v1):teal-blue (v2)
"#3bc1f0:#34caf0":5,\
#teal-blue (v1):teal-blue (v3)
"#3bc1f0:#01b0ed":1,\
#teal-blue (v1):gold (v2)
"#3bc1f0:#f9cd48":60,\
#teal-blue (v1):gold (v3)
"#3bc1f0:#fed940":65,\
#teal-blue (v1):gold (v4)
"#3bc1f0:#ffd700":70,\
#teal-blue (v1):orange (v2)
"#3bc1f0:#ffaa5f":40,\
#teal-blue (v1):light orange
"#3bc1f0:#ffae7c":35,\
#teal-blue (v1):yellow-orange
"#3bc1f0:#ffca5f":35,\
#teal-blue (v1):yellow (v1)
"#3bc1f0:#fff03a":55,\
#teal-blue (v1):yellow (v2)
"#3bc1f0:#ebdf59":50,\
#teal-blue (v1):yellow (v3)
"#3bc1f0:#f1e157":50,\
#teal-blue (v1):pink orange
"#3bc1f0:#ff9a84":35,\
#teal-blue (v1):indigo (v1)
"#3bc1f0:#c97fff":25,\
#teal-blue (v1):indigo (v2)
"#3bc1f0:#6e76ff":5,\

#teal-blue (v2):turquoise
"#34caf0:#01edd2":7,\
#teal-blue (v2):medium purple
"#34caf0:#c66aff":20,\
#teal-blue (v2):light electric pink (v1)
"#34caf0:#eb61ff":25,\
#teal-blue (v2):light electric pink (v2)
"#34caf0:#fc90ff":20,\
#teal-blue (v2):electric pink
"#34caf0:#f574ff":40,\
#teal-blue (v2):dark electric pink
"#34caf0:#ff60e1":35,\
#teal-blue (v2):coral
"#34caf0:#f88379":35,\
#teal-blue (v2):purple (v1)
"#34caf0:#977aff":15,\
#teal-blue (v2):purple (v2)
"#34caf0:#a971fc":15,\
#teal-blue (v2):purple (v3)
"#34caf0:#b76eff":20,\
#teal-blue (v2):purple (v4)
"#34caf0:#d985f7":25,\
#teal-blue (v2):purple (v5)
"#34caf0:#7f5fff":15,\
#teal-blue (v2):purple (v6)
"#34caf0:#a991ff":15,\
#teal-blue (v2):purple (v7)
"#34caf0:#a293ff":15,\
#teal-blue (v2):pink (v2)
"#34caf0:#ff7d9c":30,\
#teal-blue (v2):pink (v3)
"#34caf0:#fc98bc":40,\
#teal-blue (v2):reddish (v1)
"#34caf0:#ff5f5f":30,\
#teal-blue (v2):reddish (v2)
"#34caf0:#ff5a5a":40,\
#teal-blue (v2):tomato
"#34caf0:#ff8282":40,\
#teal-blue (v2):greenish yellow
"#34caf0:#d4d900":45,\
#teal-blue (v2):greenish
"#34caf0:#c8ff28":35,\
#teal-blue (v2):aquamarine (v1)
"#34caf0:#28ffaa":20,\
#teal-blue (v2):aquamarine (v2)
"#34caf0:#00eccb":10,\
#teal-blue (v2):firozi (v2)
"#34caf0:#2ff6ea":5,\
#teal-blue (v2):firozi (v3)
"#34caf0:#49d9ff":1,\
#teal-blue (v2):firozi (v4)
"#34caf0:#31e6ed":1,\
#teal-blue (v2):dull green
"#34caf0:#89e46c":30,\
#teal-blue (v2):mint greenish
"#34caf0:#9de245":50,\
#teal-blue (v2):mint green
"#34caf0:#66ff3a":40,\
#teal-blue (v2):light mint green
"#34caf0:#00f0a9":20,\
#teal-blue (v2):light green
"#34caf0:#a5ed31":40,\
#teal-blue (v2):green (v2)
"#34caf0:#2ff06f":30,\
#teal-blue (v2):green (v3)
"#34caf0:#26e99c":35,\
#teal-blue (v2):green (v4)
"#34caf0:#42ec72":30,\
#teal-blue (v2):green (v5)
"#34caf0:#46ec5c":35,\
#teal-blue (v2):green (v6)
"#34caf0:#50f777":30,\
#teal-blue (v2):green (v7)
"#34caf0:#01f5a1":35,\
#teal-blue (v2):green (v8)
"#34caf0:#42e966":30,\
#teal-blue (v2):green (v9)
"#34caf0:#52f578":30,\
#teal-blue (v2):sky blue (v1)
"#34caf0:#69baf5":1,\
#teal-blue (v2):sky blue (v2)
"#34caf0:#6d9eff":5,\
#teal-blue (v2):sky blue (v3)
"#34caf0:#32a8f8":7,\
#teal-blue (v2):sky blue (v4)
"#34caf0:#5caeff":7,\
#teal-blue (v2):sky blue (v5)
"#34caf0:#7ba6fc":10,\
#teal-blue (v2):blue
"#34caf0:#6292ff":7,\
#teal-blue (v2):sky-teal-blue
"#34caf0:#28d7ff":1,\
#teal-blue (v2):purple blue
"#34caf0:#9380ff":15,\
#teal-blue (v2):teal-blue (v1)
"#34caf0:#3bc1f0":5,\
#teal-blue (v2):teal-blue (v2)
"#34caf0:#34caf0":0,\
#teal-blue (v2):teal-blue (v3)
"#34caf0:#01b0ed":1,\
#teal-blue (v2):gold (v2)
"#34caf0:#f9cd48":55,\
#teal-blue (v2):gold (v3)
"#34caf0:#fed940":60,\
#teal-blue (v2):gold (v4)
"#34caf0:#ffd700":75,\
#teal-blue (v2):orange (v2)
"#34caf0:#ffaa5f":35,\
#teal-blue (v2):light orange
"#34caf0:#ffae7c":30,\
#teal-blue (v2):yellow-orange
"#34caf0:#ffca5f":35,\
#teal-blue (v2):yellow (v1)
"#34caf0:#fff03a":55,\
#teal-blue (v2):yellow (v2)
"#34caf0:#ebdf59":45,\
#teal-blue (v2):yellow (v3)
"#34caf0:#f1e157":45,\
#teal-blue (v2):pink orange
"#34caf0:#ff9a84":40,\
#teal-blue (v2):indigo (v1)
"#34caf0:#c97fff":25,\
#teal-blue (v2):indigo (v2)
"#34caf0:#6e76ff":10,\

#teal-blue (v3):turquoise
"#01b0ed:#01edd2":15,\
#teal-blue (v3):medium purple
"#01b0ed:#c66aff":50,\
#teal-blue (v3):light electric pink (v1)
"#01b0ed:#eb61ff":30,\
#teal-blue (v3):light electric pink (v2)
"#01b0ed:#fc90ff":35,\
#teal-blue (v3):electric pink
"#01b0ed:#f574ff":50,\
#teal-blue (v3):dark electric pink
"#01b0ed:#ff60e1":60,\
#teal-blue (v3):coral
"#01b0ed:#f88379":50,\
#teal-blue (v3):purple (v1)
"#01b0ed:#977aff":10,\
#teal-blue (v3):purple (v2)
"#01b0ed:#a971fc":20,\
#teal-blue (v3):purple (v3)
"#01b0ed:#b76eff":25,\
#teal-blue (v3):purple (v4)
"#01b0ed:#d985f7":55,\
#teal-blue (v3):purple (v5)
"#01b0ed:#7f5fff":20,\
#teal-blue (v3):purple (v6)
"#01b0ed:#a991ff":10,\
#teal-blue (v3):purple (v7)
"#01b0ed:#a293ff":20,\
#teal-blue (v3):pink (v2)
"#01b0ed:#ff7d9c":40,\
#teal-blue (v3):pink (v3)
"#01b0ed:#fc98bc":50,\
#teal-blue (v3):reddish (v1)
"#01b0ed:#ff5f5f":40,\
#teal-blue (v3):reddish (v2)
"#01b0ed:#ff5a5a":50,\
#teal-blue (v3):tomato
"#01b0ed:#ff8282":50,\
#teal-blue (v3):greenish yellow
"#01b0ed:#d4d900":55,\
#teal-blue (v3):greenish
"#01b0ed:#c8ff28":55,\
#teal-blue (v3):aquamarine (v1)
"#01b0ed:#28ffaa":30,\
#teal-blue (v3):aquamarine (v2)
"#01b0ed:#00eccb":15,\
#teal-blue (v3):firozi (v2)
"#01b0ed:#2ff6ea":20,\
#teal-blue (v3):firozi (v3)
"#01b0ed:#49d9ff":7,\
#teal-blue (v3):firozi (v4)
"#01b0ed:#31e6ed":5,\
#teal-blue (v3):dull green
"#01b0ed:#89e46c":45,\
#teal-blue (v3):mint greenish
"#01b0ed:#9de245":60,\
#teal-blue (v3):mint green
"#01b0ed:#66ff3a":60,\
#teal-blue (v3):light mint green
"#01b0ed:#00f0a9":30,\
#teal-blue (v3):light green
"#01b0ed:#a5ed31":65,\
#teal-blue (v3):green (v2)
"#01b0ed:#2ff06f":45,\
#teal-blue (v3):green (v3)
"#01b0ed:#26e99c":45,\
#teal-blue (v3):green (v4)
"#01b0ed:#42ec72":60,\
#teal-blue (v3):green (v5)
"#01b0ed:#46ec5c":50,\
#teal-blue (v3):green (v6)
"#01b0ed:#50f777":40,\
#teal-blue (v3):green (v7)
"#01b0ed:#01f5a1":45,\
#teal-blue (v3):green (v8)
"#01b0ed:#42e966":45,\
#teal-blue (v3):green (v9)
"#01b0ed:#52f578":55,\
#teal-blue (v3):sky blue (v1)
"#01b0ed:#69baf5":5,\
#teal-blue (v3):sky blue (v2)
"#01b0ed:#6d9eff":5,\
#teal-blue (v3):sky blue (v3)
"#01b0ed:#32a8f8":1,\
#teal-blue (v3):sky blue (v4)
"#01b0ed:#5caeff":5,\
#teal-blue (v3):sky blue (v5)
"#01b0ed:#7ba6fc":5,\
#teal-blue (v3):blue
"#01b0ed:#6292ff":5,\
#teal-blue (v3):sky-teal-blue
"#01b0ed:#28d7ff":5,\
#teal-blue (v3):purple blue
"#01b0ed:#9380ff":10,\
#teal-blue (v3):teal-blue (v1)
"#01b0ed:#3bc1f0":1,\
#teal-blue (v3):teal-blue (v2)
"#01b0ed:#34caf0":1,\
#teal-blue (v3):teal-blue (v3)
"#01b0ed:#01b0ed":0,\
#teal-blue (v3):gold (v2)
"#01b0ed:#f9cd48":45,\
#teal-blue (v3):gold (v3)
"#01b0ed:#fed940":50,\
#teal-blue (v3):gold (v4)
"#01b0ed:#ffd700":65,\
#teal-blue (v3):orange (v2)
"#01b0ed:#ffaa5f":45,\
#teal-blue (v3):light orange
"#01b0ed:#ffae7c":45,\
#teal-blue (v3):yellow-orange
"#01b0ed:#ffca5f":55,\
#teal-blue (v3):yellow (v1)
"#01b0ed:#fff03a":70,\
#teal-blue (v3):yellow (v2)
"#01b0ed:#ebdf59":55,\
#teal-blue (v3):yellow (v3)
"#01b0ed:#f1e157":55,\
#teal-blue (v3):pink orange
"#01b0ed:#ff9a84":45,\
#teal-blue (v3):indigo (v1)
"#01b0ed:#c97fff":15,\
#teal-blue (v3):indigo (v2)
"#01b0ed:#6e76ff":5,\

#gold (v2):turquoise
"#f9cd48:#01edd2":35,\
#gold (v2):medium purple
"#f9cd48:#c66aff":75,\
#gold (v2):light electric pink (v1)
"#f9cd48:#eb61ff":70,\
#gold (v2):light electric pink (v2)
"#f9cd48:#fc90ff":55,\
#gold (v2):electric pink
"#f9cd48:#f574ff":65,\
#gold (v2):dark electric pink
"#f9cd48:#ff60e1":55,\
#gold (v2):coral
"#f9cd48:#f88379":25,\
#gold (v2):purple (v1)
"#f9cd48:#977aff":55,\
#gold (v2):purple (v2)
"#f9cd48:#a971fc":70,\
#gold (v2):purple (v3)
"#f9cd48:#b76eff":65,\
#gold (v2):purple (v4)
"#f9cd48:#d985f7":40,\
#gold (v2):purple (v5)
"#f9cd48:#7f5fff":50,\
#gold (v2):purple (v6)
"#f9cd48:#a991ff":45,\
#gold (v2):purple (v7)
"#f9cd48:#a293ff":50,\
#gold (v2):pink (v2)
"#f9cd48:#ff7d9c":30,\
#gold (v2):pink (v3)
"#f9cd48:#fc98bc":35,\
#gold (v2):reddish (v1)
"#f9cd48:#ff5f5f":35,\
#gold (v2):reddish (v2)
"#f9cd48:#ff5a5a":30,\
#gold (v2):tomato
"#f9cd48:#ff8282":25,\
#gold (v2):greenish yellow
"#f9cd48:#d4d900":10,\
#gold (v2):greenish
"#f9cd48:#c8ff28":10,\
#gold (v2):aquamarine (v1)
"#f9cd48:#28ffaa":30,\
#gold (v2):aquamarine (v2)
"#f9cd48:#00eccb":40,\
#gold (v2):firozi (v2)
"#f9cd48:#2ff6ea":45,\
#gold (v2):firozi (v3)
"#f9cd48:#49d9ff":30,\
#gold (v2):firozi (v4)
"#f9cd48:#31e6ed":35,\
#gold (v2):dull green
"#f9cd48:#89e46c":25,\
#gold (v2):mint greenish
"#f9cd48:#9de245":40,\
#gold (v2):mint green
"#f9cd48:#66ff3a":25,\
#gold (v2):light mint green
"#f9cd48:#00f0a9":45,\
#gold (v2):light green
"#f9cd48:#a5ed31":20,\
#gold (v2):green (v2)
"#f9cd48:#2ff06f":30,\
#gold (v2):green (v3)
"#f9cd48:#26e99c":40,\
#gold (v2):green (v4)
"#f9cd48:#42ec72":25,\
#gold (v2):green (v5)
"#f9cd48:#46ec5c":30,\
#gold (v2):green (v6)
"#f9cd48:#50f777":25,\
#gold (v2):green (v7)
"#f9cd48:#01f5a1":40,\
#gold (v2):green (v8)
"#f9cd48:#42e966":35,\
#gold (v2):green (v9)
"#f9cd48:#52f578":25,\
#gold (v2):sky blue (v1)
"#f9cd48:#69baf5":45,\
#gold (v2):sky blue (v2)
"#f9cd48:#6d9eff":45,\
#gold (v2):sky blue (v3)
"#f9cd48:#32a8f8":45,\
#gold (v2):sky blue (v4)
"#f9cd48:#5caeff":45,\
#gold (v2):sky blue (v5)
"#f9cd48:#7ba6fc":45,\
#gold (v2):blue
"#f9cd48:#6292ff":50,\
#gold (v2):sky-teal-blue
"#f9cd48:#28d7ff":35,\
#gold (v2):purple blue
"#f9cd48:#9380ff":50,\
#gold (v2):teal-blue (v1)
"#f9cd48:#3bc1f0":60,\
#gold (v2):teal-blue (v2)
"#f9cd48:#34caf0":55,\
#gold (v2):teal-blue (v3)
"#f9cd48:#01b0ed":45,\
#gold (v2):gold (v2)
"#f9cd48:#f9cd48":0,\
#gold (v2):gold (v3)
"#f9cd48:#fed940":1,\
#gold (v2):gold (v4)
"#f9cd48:#ffd700":5,\
#gold (v2):orange (v2)
"#f9cd48:#ffaa5f":7,\
#gold (v2):light orange
"#f9cd48:#ffae7c":7,\
#gold (v2):yellow-orange
"#f9cd48:#ffca5f":1,\
#gold (v2):yellow (v1)
"#f9cd48:#fff03a":5,\
#gold (v2):yellow (v2)
"#f9cd48:#ebdf59":1,\
#gold (v2):yellow (v3)
"#f9cd48:#f1e157":1,\
#gold (v2):pink orange
"#f9cd48:#ff9a84":10,\
#gold (v2):indigo (v1)
"#f9cd48:#c97fff":45,\
#gold (v2):indigo (v2)
"#f9cd48:#6e76ff":70,\

#gold (v3):turquoise
"#fed940:#01edd2":30,\
#gold (v3):medium purple
"#fed940:#c66aff":75,\
#gold (v3):light electric pink (v1)
"#fed940:#eb61ff":75,\
#gold (v3):light electric pink (v2)
"#fed940:#fc90ff":55,\
#gold (v3):electric pink
"#fed940:#f574ff":60,\
#gold (v3):dark electric pink
"#fed940:#ff60e1":55,\
#gold (v3):coral
"#fed940:#f88379":25,\
#gold (v3):purple (v1)
"#fed940:#977aff":50,\
#gold (v3):purple (v2)
"#fed940:#a971fc":75,\
#gold (v3):purple (v3)
"#fed940:#b76eff":60,\
#gold (v3):purple (v4)
"#fed940:#d985f7":40,\
#gold (v3):purple (v5)
"#fed940:#7f5fff":50,\
#gold (v3):purple (v6)
"#fed940:#a991ff":40,\
#gold (v3):purple (v7)
"#fed940:#a293ff":45,\
#gold (v3):pink (v2)
"#fed940:#ff7d9c":30,\
#gold (v3):pink (v3)
"#fed940:#fc98bc":35,\
#gold (v3):reddish (v1)
"#fed940:#ff5f5f":35,\
#gold (v3):reddish (v2)
"#fed940:#ff5a5a":30,\
#gold (v3):tomato
"#fed940:#ff8282":20,\
#gold (v3):greenish yellow
"#fed940:#d4d900":7,\
#gold (v3):greenish
"#fed940:#c8ff28":10,\
#gold (v3):aquamarine (v1)
"#fed940:#28ffaa":30,\
#gold (v3):aquamarine (v2)
"#fed940:#00eccb":40,\
#gold (v3):firozi (v2)
"#fed940:#2ff6ea":45,\
#gold (v3):firozi (v3)
"#fed940:#49d9ff":30,\
#gold (v3):firozi (v4)
"#fed940:#31e6ed":35,\
#gold (v3):dull green
"#fed940:#89e46c":20,\
#gold (v3):mint greenish
"#fed940:#9de245":40,\
#gold (v3):mint green
"#fed940:#66ff3a":20,\
#gold (v3):light mint green
"#fed940:#00f0a9":45,\
#gold (v3):light green
"#fed940:#a5ed31":20,\
#gold (v3):green (v2)
"#fed940:#2ff06f":25,\
#gold (v3):green (v3)
"#fed940:#26e99c":40,\
#gold (v3):green (v4)
"#fed940:#42ec72":20,\
#gold (v3):green (v5)
"#fed940:#46ec5c":30,\
#gold (v3):green (v6)
"#fed940:#50f777":25,\
#gold (v3):green (v7)
"#fed940:#01f5a1":40,\
#gold (v3):green (v8)
"#fed940:#42e966":30,\
#gold (v3):green (v9)
"#fed940:#52f578":25,\
#gold (v3):sky blue (v1)
"#fed940:#69baf5":45,\
#gold (v3):sky blue (v2)
"#fed940:#6d9eff":45,\
#gold (v3):sky blue (v3)
"#fed940:#32a8f8":45,\
#gold (v3):sky blue (v4)
"#fed940:#5caeff":50,\
#gold (v3):sky blue (v5)
"#fed940:#7ba6fc":45,\
#gold (v3):blue
"#fed940:#6292ff":60,\
#gold (v3):sky-teal-blue
"#fed940:#28d7ff":40,\
#gold (v3):purple blue
"#fed940:#9380ff":50,\
#gold (v3):teal-blue (v1)
"#fed940:#3bc1f0":65,\
#gold (v3):teal-blue (v2)
"#fed940:#34caf0":60,\
#gold (v3):teal-blue (v3)
"#fed940:#01b0ed":50,\
#gold (v3):gold (v2)
"#fed940:#f9cd48":1,\
#gold (v3):gold (v3)
"#fed940:#fed940":0,\
#gold (v3):gold (v4)
"#fed940:#ffd700":1,\
#gold (v3):orange (v2)
"#fed940:#ffaa5f":10,\
#gold (v3):light orange
"#fed940:#ffae7c":10,\
#gold (v3):yellow-orange
"#fed940:#ffca5f":5,\
#gold (v3):yellow (v1)
"#fed940:#fff03a":5,\
#gold (v3):yellow (v2)
"#fed940:#ebdf59":5,\
#gold (v3):yellow (v3)
"#fed940:#f1e157":5,\
#gold (v3):pink orange
"#fed940:#ff9a84":20,\
#gold (v3):indigo (v1)
"#fed940:#c97fff":55,\
#gold (v3):indigo (v2)
"#fed940:#6e76ff":65,\

#gold (v4):turquoise
"#ffd700:#01edd2":55,\
#gold (v4):medium purple
"#ffd700:#c66aff":80,\
#gold (v4):light electric pink (v1)
"#ffd700:#eb61ff":80,\
#gold (v4):light electric pink (v2)
"#ffd700:#fc90ff":65,\
#gold (v4):electric pink
"#ffd700:#f574ff":80,\
#gold (v4):dark electric pink
"#ffd700:#ff60e1":80,\
#gold (v4):coral
"#ffd700:#f88379":30,\
#gold (v4):purple (v1)
"#ffd700:#977aff":65,\
#gold (v4):purple (v2)
"#ffd700:#a971fc":85,\
#gold (v4):purple (v3)
"#ffd700:#b76eff":70,\
#gold (v4):purple (v4)
"#ffd700:#d985f7":50,\
#gold (v4):purple (v5)
"#ffd700:#7f5fff":80,\
#gold (v4):purple (v6)
"#ffd700:#a991ff":55,\
#gold (v4):purple (v7)
"#ffd700:#a293ff":70,\
#gold (v4):pink (v2)
"#ffd700:#ff7d9c":55,\
#gold (v4):pink (v3)
"#ffd700:#fc98bc":45,\
#gold (v4):reddish (v1)
"#ffd700:#ff5f5f":55,\
#gold (v4):reddish (v2)
"#ffd700:#ff5a5a":40,\
#gold (v4):tomato
"#ffd700:#ff8282":35,\
#gold (v4):greenish yellow
"#ffd700:#d4d900":10,\
#gold (v4):greenish
"#ffd700:#c8ff28":15,\
#gold (v4):aquamarine (v1)
"#ffd700:#28ffaa":45,\
#gold (v4):aquamarine (v2)
"#ffd700:#00eccb":55,\
#gold (v4):firozi (v2)
"#ffd700:#2ff6ea":50,\
#gold (v4):firozi (v3)
"#ffd700:#49d9ff":40,\
#gold (v4):firozi (v4)
"#ffd700:#31e6ed":45,\
#gold (v4):dull green
"#ffd700:#89e46c":30,\
#gold (v4):mint greenish
"#ffd700:#9de245":45,\
#gold (v4):mint green
"#ffd700:#66ff3a":25,\
#gold (v4):light mint green
"#ffd700:#00f0a9":55,\
#gold (v4):light green
"#ffd700:#a5ed31":25,\
#gold (v4):green (v2)
"#ffd700:#2ff06f":35,\
#gold (v4):green (v3)
"#ffd700:#26e99c":50,\
#gold (v4):green (v4)
"#ffd700:#42ec72":35,\
#gold (v4):green (v5)
"#ffd700:#46ec5c":40,\
#gold (v4):green (v6)
"#ffd700:#50f777":35,\
#gold (v4):green (v7)
"#ffd700:#01f5a1":55,\
#gold (v4):green (v8)
"#ffd700:#42e966":45,\
#gold (v4):green (v9)
"#ffd700:#52f578":35,\
#gold (v4):sky blue (v1)
"#ffd700:#69baf5":60,\
#gold (v4):sky blue (v2)
"#ffd700:#6d9eff":60,\
#gold (v4):sky blue (v3)
"#ffd700:#32a8f8":65,\
#gold (v4):sky blue (v4)
"#ffd700:#5caeff":65,\
#gold (v4):sky blue (v5)
"#ffd700:#7ba6fc":70,\
#gold (v4):blue
"#ffd700:#6292ff":75,\
#gold (v4):sky-teal-blue
"#ffd700:#28d7ff":65,\
#gold (v4):purple blue
"#ffd700:#9380ff":70,\
#gold (v4):teal-blue (v1)
"#ffd700:#3bc1f0":70,\
#gold (v4):teal-blue (v2)
"#ffd700:#34caf0":75,\
#gold (v4):teal-blue (v3)
"#ffd700:#01b0ed":65,\
#gold (v4):gold (v2)
"#ffd700:#f9cd48":5,\
#gold (v4):gold (v3)
"#ffd700:#fed940":1,\
#gold (v4):gold (v4)
"#ffd700:#ffd700":0,\
#gold (v4):orange (v2)
"#ffd700:#ffaa5f":5,\
#gold (v4):light orange
"#ffd700:#ffae7c":5,\
#gold (v4):yellow-orange
"#ffd700:#ffca5f":1,\
#gold (v4):yellow (v1)
"#ffd700:#fff03a":1,\
#gold (v4):yellow (v2)
"#ffd700:#ebdf59":5,\
#gold (v4):yellow (v3)
"#ffd700:#f1e157":5,\
#gold (v4):pink orange
"#ffd700:#ff9a84":10,\
#gold (v4):indigo (v1)
"#ffd700:#c97fff":65,\
#gold (v4):indigo (v2)
"#ffd700:#6e76ff":75,\

#orange (v2):turquoise
"#ffaa5f:#01edd2":45,\
#orange (v2):medium purple
"#ffaa5f:#c66aff":60,\
#orange (v2):light electric pink (v1)
"#ffaa5f:#eb61ff":50,\
#orange (v2):light electric pink (v2)
"#ffaa5f:#fc90ff":30,\
#orange (v2):electric pink
"#ffaa5f:#f574ff":50,\
#orange (v2):dark electric pink
"#ffaa5f:#ff60e1":45,\
#orange (v2):coral
"#ffaa5f:#f88379":10,\
#orange (v2):purple (v1)
"#ffaa5f:#977aff":45,\
#orange (v2):purple (v2)
"#ffaa5f:#a971fc":60,\
#orange (v2):purple (v3)
"#ffaa5f:#b76eff":55,\
#orange (v2):purple (v4)
"#ffaa5f:#d985f7":30,\
#orange (v2):purple (v5)
"#ffaa5f:#7f5fff":50,\
#orange (v2):purple (v6)
"#ffaa5f:#a991ff":35,\
#orange (v2):purple (v7)
"#ffaa5f:#a293ff":40,\
#orange (v2):pink (v2)
"#ffaa5f:#ff7d9c":15,\
#orange (v2):pink (v3)
"#ffaa5f:#fc98bc":20,\
#orange (v2):reddish (v1)
"#ffaa5f:#ff5f5f":10,\
#orange (v2):reddish (v2)
"#ffaa5f:#ff5a5a":10,\
#orange (v2):tomato
"#ffaa5f:#ff8282":15,\
#orange (v2):greenish yellow
"#ffaa5f:#d4d900":15,\
#orange (v2):greenish
"#ffaa5f:#c8ff28":20,\
#orange (v2):aquamarine (v1)
"#ffaa5f:#28ffaa":40,\
#orange (v2):aquamarine (v2)
"#ffaa5f:#00eccb":35,\
#orange (v2):firozi (v2)
"#ffaa5f:#2ff6ea":35,\
#orange (v2):firozi (v3)
"#ffaa5f:#49d9ff":30,\
#orange (v2):firozi (v4)
"#ffaa5f:#31e6ed":40,\
#orange (v2):dull green
"#ffaa5f:#89e46c":40,\
#orange (v2):mint greenish
"#ffaa5f:#9de245":25,\
#orange (v2):mint green
"#ffaa5f:#66ff3a":25,\
#orange (v2):light mint green
"#ffaa5f:#00f0a9":40,\
#orange (v2):light green
"#ffaa5f:#a5ed31":25,\
#orange (v2):green (v2)
"#ffaa5f:#2ff06f":30,\
#orange (v2):green (v3)
"#ffaa5f:#26e99c":25,\
#orange (v2):green (v4)
"#ffaa5f:#42ec72":25,\
#orange (v2):green (v5)
"#ffaa5f:#46ec5c":35,\
#orange (v2):green (v6)
"#ffaa5f:#50f777":30,\
#orange (v2):green (v7)
"#ffaa5f:#01f5a1":30,\
#orange (v2):green (v8)
"#ffaa5f:#42e966":35,\
#orange (v2):green (v9)
"#ffaa5f:#52f578":30,\
#orange (v2):sky blue (v1)
"#ffaa5f:#69baf5":45,\
#orange (v2):sky blue (v2)
"#ffaa5f:#6d9eff":25,\
#orange (v2):sky blue (v3)
"#ffaa5f:#32a8f8":35,\
#orange (v2):sky blue (v4)
"#ffaa5f:#5caeff":45,\
#orange (v2):sky blue (v5)
"#ffaa5f:#7ba6fc":35,\
#orange (v2):blue
"#ffaa5f:#6292ff":40,\
#orange (v2):sky-teal-blue
"#ffaa5f:#28d7ff":40,\
#orange (v2):purple blue
"#ffaa5f:#9380ff":45,\
#orange (v2):teal-blue (v1)
"#ffaa5f:#3bc1f0":40,\
#orange (v2):teal-blue (v2)
"#ffaa5f:#34caf0":35,\
#orange (v2):teal-blue (v3)
"#ffaa5f:#01b0ed":45,\
#orange (v2):gold (v2)
"#ffaa5f:#f9cd48":7,\
#orange (v2):gold (v3)
"#ffaa5f:#fed940":10,\
#orange (v2):gold (v4)
"#ffaa5f:#ffd700":5,\
#orange (v2):orange (v2)
"#ffaa5f:#ffaa5f":0,\
#orange (v2):light orange
"#ffaa5f:#ffae7c":1,\
#orange (v2):yellow-orange
"#ffaa5f:#ffca5f":5,\
#orange (v2):yellow (v1)
"#ffaa5f:#fff03a":15,\
#orange (v2):yellow (v2)
"#ffaa5f:#ebdf59":10,\
#orange (v2):yellow (v3)
"#ffaa5f:#f1e157":10,\
#orange (v2):pink orange
"#ffaa5f:#ff9a84":5,\
#orange (v2):indigo (v1)
"#ffaa5f:#c97fff":45,\
#orange (v2):indigo (v2)
"#ffaa5f:#6e76ff":60,\

#light orange:turquoise
"#ffae7c:#01edd2":35,\
#light orange:medium purple
"#ffae7c:#c66aff":55,\
#light orange:light electric pink (v1)
"#ffae7c:#eb61ff":40,\
#light orange:light electric pink (v2)
"#ffae7c:#fc90ff":25,\
#light orange:electric pink
"#ffae7c:#f574ff":40,\
#light orange:dark electric pink
"#ffae7c:#ff60e1":40,\
#light orange:coral
"#ffae7c:#f88379":7,\
#light orange:purple (v1)
"#ffae7c:#977aff":40,\
#light orange:purple (v2)
"#ffae7c:#a971fc":55,\
#light orange:purple (v3)
"#ffae7c:#b76eff":50,\
#light orange:purple (v4)
"#ffae7c:#d985f7":25,\
#light orange:purple (v5)
"#ffae7c:#7f5fff":45,\
#light orange:purple (v6)
"#ffae7c:#a991ff":30,\
#light orange:purple (v7)
"#ffae7c:#a293ff":40,\
#light orange:pink (v2)
"#ffae7c:#ff7d9c":15,\
#light orange:pink (v3)
"#ffae7c:#fc98bc":20,\
#light orange:reddish (v1)
"#ffae7c:#ff5f5f":15,\
#light orange:reddish (v2)
"#ffae7c:#ff5a5a":15,\
#light orange:tomato
"#ffae7c:#ff8282":10,\
#light orange:greenish yellow
"#ffae7c:#d4d900":15,\
#light orange:greenish
"#ffae7c:#c8ff28":20,\
#light orange:aquamarine (v1)
"#ffae7c:#28ffaa":40,\
#light orange:aquamarine (v2)
"#ffae7c:#00eccb":30,\
#light orange:firozi (v2)
"#ffae7c:#2ff6ea":30,\
#light orange:firozi (v3)
"#ffae7c:#49d9ff":30,\
#light orange:firozi (v4)
"#ffae7c:#31e6ed":40,\
#light orange:dull green
"#ffae7c:#89e46c":40,\
#light orange:mint greenish
"#ffae7c:#9de245":25,\
#light orange:mint green
"#ffae7c:#66ff3a":25,\
#light orange:light mint green
"#ffae7c:#00f0a9":35,\
#light orange:light green
"#ffae7c:#a5ed31":25,\
#light orange:green (v2)
"#ffae7c:#2ff06f":30,\
#light orange:green (v3)
"#ffae7c:#26e99c":25,\
#light orange:green (v4)
"#ffae7c:#42ec72":25,\
#light orange:green (v5)
"#ffae7c:#46ec5c":35,\
#light orange:green (v6)
"#ffae7c:#50f777":30,\
#light orange:green (v7)
"#ffae7c:#01f5a1":25,\
#light orange:green (v8)
"#ffae7c:#42e966":30,\
#light orange:green (v9)
"#ffae7c:#52f578":30,\
#light orange:sky blue (v1)
"#ffae7c:#69baf5":40,\
#light orange:sky blue (v2)
"#ffae7c:#6d9eff":25,\
#light orange:sky blue (v3)
"#ffae7c:#32a8f8":30,\
#light orange:sky blue (v4)
"#ffae7c:#5caeff":40,\
#light orange:sky blue (v5)
"#ffae7c:#7ba6fc":30,\
#light orange:blue
"#ffae7c:#6292ff":40,\
#light orange:sky-teal-blue
"#ffae7c:#28d7ff":40,\
#light orange:purple blue
"#ffae7c:#9380ff":40,\
#light orange:teal-blue (v1)
"#ffae7c:#3bc1f0":35,\
#light orange:teal-blue (v2)
"#ffae7c:#34caf0":30,\
#light orange:teal-blue (v3)
"#ffae7c:#01b0ed":45,\
#light orange:gold (v2)
"#ffae7c:#f9cd48":7,\
#light orange:gold (v3)
"#ffae7c:#fed940":10,\
#light orange:gold (v4)
"#ffae7c:#ffd700":5,\
#light orange:orange (v2)
"#ffae7c:#ffaa5f":1,\
#light orange:light orange
"#ffae7c:#ffae7c":0,\
#light orange:yellow-orange
"#ffae7c:#ffca5f":5,\
#light orange:yellow (v1)
"#ffae7c:#fff03a":15,\
#light orange:yellow (v2)
"#ffae7c:#ebdf59":10,\
#light orange:yellow (v3)
"#ffae7c:#f1e157":10,\
#light orange:pink orange
"#ffae7c:#ff9a84":1,\
#light orange:indigo (v1)
"#ffae7c:#c97fff":35,\
#light orange:indigo (v2)
"#ffae7c:#6e76ff":55,\

#yellow-orange:turquoise
"#ffca5f:#01edd2":40,\
#yellow-orange:medium purple
"#ffca5f:#c66aff":65,\
#yellow-orange:light electric pink (v1)
"#ffca5f:#eb61ff":45,\
#yellow-orange:light electric pink (v2)
"#ffca5f:#fc90ff":30,\
#yellow-orange:electric pink
"#ffca5f:#f574ff":30,\
#yellow-orange:dark electric pink
"#ffca5f:#ff60e1":45,\
#yellow-orange:coral
"#ffca5f:#f88379":10,\
#yellow-orange:purple (v1)
"#ffca5f:#977aff":35,\
#yellow-orange:purple (v2)
"#ffca5f:#a971fc":45,\
#yellow-orange:purple (v3)
"#ffca5f:#b76eff":45,\
#yellow-orange:purple (v4)
"#ffca5f:#d985f7":25,\
#yellow-orange:purple (v5)
"#ffca5f:#7f5fff":40,\
#yellow-orange:purple (v6)
"#ffca5f:#a991ff":40,\
#yellow-orange:purple (v7)
"#ffca5f:#a293ff":45,\
#yellow-orange:pink (v2)
"#ffca5f:#ff7d9c":20,\
#yellow-orange:pink (v3)
"#ffca5f:#fc98bc":20,\
#yellow-orange:reddish (v1)
"#ffca5f:#ff5f5f":15,\
#yellow-orange:reddish (v2)
"#ffca5f:#ff5a5a":20,\
#yellow-orange:tomato
"#ffca5f:#ff8282":15,\
#yellow-orange:greenish yellow
"#ffca5f:#d4d900":10,\
#yellow-orange:greenish
"#ffca5f:#c8ff28":15,\
#yellow-orange:aquamarine (v1)
"#ffca5f:#28ffaa":35,\
#yellow-orange:aquamarine (v2)
"#ffca5f:#00eccb":30,\
#yellow-orange:firozi (v2)
"#ffca5f:#2ff6ea":25,\
#yellow-orange:firozi (v3)
"#ffca5f:#49d9ff":35,\
#yellow-orange:firozi (v4)
"#ffca5f:#31e6ed":45,\
#yellow-orange:dull green
"#ffca5f:#89e46c":25,\
#yellow-orange:mint greenish
"#ffca5f:#9de245":15,\
#yellow-orange:mint green
"#ffca5f:#66ff3a":20,\
#yellow-orange:light mint green
"#ffca5f:#00f0a9":35,\
#yellow-orange:light green
"#ffca5f:#a5ed31":15,\
#yellow-orange:green (v2)
"#ffca5f:#2ff06f":30,\
#yellow-orange:green (v3)
"#ffca5f:#26e99c":30,\
#yellow-orange:green (v4)
"#ffca5f:#42ec72":20,\
#yellow-orange:green (v5)
"#ffca5f:#46ec5c":25,\
#yellow-orange:green (v6)
"#ffca5f:#50f777":20,\
#yellow-orange:green (v7)
"#ffca5f:#01f5a1":30,\
#yellow-orange:green (v8)
"#ffca5f:#42e966":25,\
#yellow-orange:green (v9)
"#ffca5f:#52f578":20,\
#yellow-orange:sky blue (v1)
"#ffca5f:#69baf5":40,\
#yellow-orange:sky blue (v2)
"#ffca5f:#6d9eff":40,\
#yellow-orange:sky blue (v3)
"#ffca5f:#32a8f8":40,\
#yellow-orange:sky blue (v4)
"#ffca5f:#5caeff":30,\
#yellow-orange:sky blue (v5)
"#ffca5f:#7ba6fc":40,\
#yellow-orange:blue
"#ffca5f:#6292ff":45,\
#yellow-orange:sky-teal-blue
"#ffca5f:#28d7ff":45,\
#yellow-orange:purple blue
"#ffca5f:#9380ff":30,\
#yellow-orange:teal-blue (v1)
"#ffca5f:#3bc1f0":35,\
#yellow-orange:teal-blue (v2)
"#ffca5f:#34caf0":35,\
#yellow-orange:teal-blue (v3)
"#ffca5f:#01b0ed":55,\
#yellow-orange:gold (v2)
"#ffca5f:#f9cd48":1,\
#yellow-orange:gold (v3)
"#ffca5f:#fed940":5,\
#yellow-orange:gold (v4)
"#ffca5f:#ffd700":1,\
#yellow-orange:orange (v2)
"#ffca5f:#ffaa5f":5,\
#yellow-orange:light orange
"#ffca5f:#ffae7c":5,\
#yellow-orange:yellow-orange
"#ffca5f:#ffca5f":0,\
#yellow-orange:yellow (v1)
"#ffca5f:#fff03a":7,\
#yellow-orange:yellow (v2)
"#ffca5f:#ebdf59":1,\
#yellow-orange:yellow (v3)
"#ffca5f:#f1e157":1,\
#yellow-orange:pink orange
"#ffca5f:#ff9a84":15,\
#yellow-orange:indigo (v1)
"#ffca5f:#c97fff":45,\
#yellow-orange:indigo (v2)
"#ffca5f:#6e76ff":65,\

#yellow (v1):turquoise
"#fff03a:#01edd2":30,\
#yellow (v1):medium purple
"#fff03a:#c66aff":70,\
#yellow (v1):light electric pink (v1)
"#fff03a:#eb61ff":35,\
#yellow (v1):light electric pink (v2)
"#fff03a:#fc90ff":20,\
#yellow (v1):electric pink
"#fff03a:#f574ff":20,\
#yellow (v1):dark electric pink
"#fff03a:#ff60e1":35,\
#yellow (v1):coral
"#fff03a:#f88379":15,\
#yellow (v1):purple (v1)
"#fff03a:#977aff":25,\
#yellow (v1):purple (v2)
"#fff03a:#a971fc":30,\
#yellow (v1):purple (v3)
"#fff03a:#b76eff":60,\
#yellow (v1):purple (v4)
"#fff03a:#d985f7":35,\
#yellow (v1):purple (v5)
"#fff03a:#7f5fff":45,\
#yellow (v1):purple (v6)
"#fff03a:#a991ff":40,\
#yellow (v1):purple (v7)
"#fff03a:#a293ff":35,\
#yellow (v1):pink (v2)
"#fff03a:#ff7d9c":30,\
#yellow (v1):pink (v3)
"#fff03a:#fc98bc":15,\
#yellow (v1):reddish (v1)
"#fff03a:#ff5f5f":25,\
#yellow (v1):reddish (v2)
"#fff03a:#ff5a5a":25,\
#yellow (v1):tomato
"#fff03a:#ff8282":20,\
#yellow (v1):greenish yellow
"#fff03a:#d4d900":1,\
#yellow (v1):greenish
"#fff03a:#c8ff28":5,\
#yellow (v1):aquamarine (v1)
"#fff03a:#28ffaa":20,\
#yellow (v1):aquamarine (v2)
"#fff03a:#00eccb":25,\
#yellow (v1):firozi (v2)
"#fff03a:#2ff6ea":25,\
#yellow (v1):firozi (v3)
"#fff03a:#49d9ff":30,\
#yellow (v1):firozi (v4)
"#fff03a:#31e6ed":35,\
#yellow (v1):dull green
"#fff03a:#89e46c":20,\
#yellow (v1):mint greenish
"#fff03a:#9de245":10,\
#yellow (v1):mint green
"#fff03a:#66ff3a":10,\
#yellow (v1):light mint green
"#fff03a:#00f0a9":25,\
#yellow (v1):light green
"#fff03a:#a5ed31":5,\
#yellow (v1):green (v2)
"#fff03a:#2ff06f":25,\
#yellow (v1):green (v3)
"#fff03a:#26e99c":30,\
#yellow (v1):green (v4)
"#fff03a:#42ec72":15,\
#yellow (v1):green (v5)
"#fff03a:#46ec5c":20,\
#yellow (v1):green (v6)
"#fff03a:#50f777":15,\
#yellow (v1):green (v7)
"#fff03a:#01f5a1":20,\
#yellow (v1):green (v8)
"#fff03a:#42e966":15,\
#yellow (v1):green (v9)
"#fff03a:#52f578":15,\
#yellow (v1):sky blue (v1)
"#fff03a:#69baf5":50,\
#yellow (v1):sky blue (v2)
"#fff03a:#6d9eff":65,\
#yellow (v1):sky blue (v3)
"#fff03a:#32a8f8":60,\
#yellow (v1):sky blue (v4)
"#fff03a:#5caeff":40,\
#yellow (v1):sky blue (v5)
"#fff03a:#7ba6fc":55,\
#yellow (v1):blue
"#fff03a:#6292ff":55,\
#yellow (v1):sky-teal-blue
"#fff03a:#28d7ff":55,\
#yellow (v1):purple blue
"#fff03a:#9380ff":70,\
#yellow (v1):teal-blue (v1)
"#fff03a:#3bc1f0":55,\
#yellow (v1):teal-blue (v2)
"#fff03a:#34caf0":55,\
#yellow (v1):teal-blue (v3)
"#fff03a:#01b0ed":70,\
#yellow (v1):gold (v2)
"#fff03a:#f9cd48":5,\
#yellow (v1):gold (v3)
"#fff03a:#fed940":5,\
#yellow (v1):gold (v4)
"#fff03a:#ffd700":1,\
#yellow (v1):orange (v2)
"#fff03a:#ffaa5f":15,\
#yellow (v1):light orange
"#fff03a:#ffae7c":15,\
#yellow (v1):yellow-orange
"#fff03a:#ffca5f":7,\
#yellow (v1):yellow (v1)
"#fff03a:#fff03a":0,\
#yellow (v1):yellow (v2)
"#fff03a:#ebdf59":5,\
#yellow (v1):yellow (v3)
"#fff03a:#f1e157":5,\
#yellow (v1):pink orange
"#fff03a:#ff9a84":15,\
#yellow (v1):indigo (v1)
"#fff03a:#c97fff":30,\
#yellow (v1):indigo (v2)
"#fff03a:#6e76ff":50,\

#yellow (v2):turquoise
"#ebdf59:#01edd2":35,\
#yellow (v2):medium purple
"#ebdf59:#c66aff":75,\
#yellow (v2):light electric pink (v1)
"#ebdf59:#eb61ff":45,\
#yellow (v2):light electric pink (v2)
"#ebdf59:#fc90ff":30,\
#yellow (v2):electric pink
"#ebdf59:#f574ff":30,\
#yellow (v2):dark electric pink
"#ebdf59:#ff60e1":40,\
#yellow (v2):coral
"#ebdf59:#f88379":20,\
#yellow (v2):purple (v1)
"#ebdf59:#977aff":30,\
#yellow (v2):purple (v2)
"#ebdf59:#a971fc":35,\
#yellow (v2):purple (v3)
"#ebdf59:#b76eff":40,\
#yellow (v2):purple (v4)
"#ebdf59:#d985f7":35,\
#yellow (v2):purple (v5)
"#ebdf59:#7f5fff":35,\
#yellow (v2):purple (v6)
"#ebdf59:#a991ff":30,\
#yellow (v2):purple (v7)
"#ebdf59:#a293ff":40,\
#yellow (v2):pink (v2)
"#ebdf59:#ff7d9c":30,\
#yellow (v2):pink (v3)
"#ebdf59:#fc98bc":15,\
#yellow (v2):reddish (v1)
"#ebdf59:#ff5f5f":30,\
#yellow (v2):reddish (v2)
"#ebdf59:#ff5a5a":30,\
#yellow (v2):tomato
"#ebdf59:#ff8282":25,\
#yellow (v2):greenish yellow
"#ebdf59:#d4d900":1,\
#yellow (v2):greenish
"#ebdf59:#c8ff28":5,\
#yellow (v2):aquamarine (v1)
"#ebdf59:#28ffaa":15,\
#yellow (v2):aquamarine (v2)
"#ebdf59:#00eccb":25,\
#yellow (v2):firozi (v2)
"#ebdf59:#2ff6ea":20,\
#yellow (v2):firozi (v3)
"#ebdf59:#49d9ff":30,\
#yellow (v2):firozi (v4)
"#ebdf59:#31e6ed":40,\
#yellow (v2):dull green
"#ebdf59:#89e46c":15,\
#yellow (v2):mint greenish
"#ebdf59:#9de245":7,\
#yellow (v2):mint green
"#ebdf59:#66ff3a":15,\
#yellow (v2):light mint green
"#ebdf59:#00f0a9":30,\
#yellow (v2):light green
"#ebdf59:#a5ed31":7,\
#yellow (v2):green (v2)
"#ebdf59:#2ff06f":20,\
#yellow (v2):green (v3)
"#ebdf59:#26e99c":35,\
#yellow (v2):green (v4)
"#ebdf59:#42ec72":20,\
#yellow (v2):green (v5)
"#ebdf59:#46ec5c":20,\
#yellow (v2):green (v6)
"#ebdf59:#50f777":20,\
#yellow (v2):green (v7)
"#ebdf59:#01f5a1":25,\
#yellow (v2):green (v8)
"#ebdf59:#42e966":20,\
#yellow (v2):green (v9)
"#ebdf59:#52f578":20,\
#yellow (v2):sky blue (v1)
"#ebdf59:#69baf5":45,\
#yellow (v2):sky blue (v2)
"#ebdf59:#6d9eff":55,\
#yellow (v2):sky blue (v3)
"#ebdf59:#32a8f8":40,\
#yellow (v2):sky blue (v4)
"#ebdf59:#5caeff":25,\
#yellow (v2):sky blue (v5)
"#ebdf59:#7ba6fc":35,\
#yellow (v2):blue
"#ebdf59:#6292ff":45,\
#yellow (v2):sky-teal-blue
"#ebdf59:#28d7ff":45,\
#yellow (v2):purple blue
"#ebdf59:#9380ff":60,\
#yellow (v2):teal-blue (v1)
"#ebdf59:#3bc1f0":50,\
#yellow (v2):teal-blue (v2)
"#ebdf59:#34caf0":45,\
#yellow (v2):teal-blue (v3)
"#ebdf59:#01b0ed":55,\
#yellow (v2):gold (v2)
"#ebdf59:#f9cd48":1,\
#yellow (v2):gold (v3)
"#ebdf59:#fed940":5,\
#yellow (v2):gold (v4)
"#ebdf59:#ffd700":5,\
#yellow (v2):orange (v2)
"#ebdf59:#ffaa5f":10,\
#yellow (v2):light orange
"#ebdf59:#ffae7c":10,\
#yellow (v2):yellow-orange
"#ebdf59:#ffca5f":1,\
#yellow (v2):yellow (v1)
"#ebdf59:#fff03a":5,\
#yellow (v2):yellow (v2)
"#ebdf59:#ebdf59":0,\
#yellow (v2):yellow (v3)
"#ebdf59:#f1e157":1,\
#yellow (v2):pink orange
"#ebdf59:#ff9a84":15,\
#yellow (v2):indigo (v1)
"#ebdf59:#c97fff":40,\
#yellow (v2):indigo (v2)
"#ebdf59:#6e76ff":65,\

#yellow (v3):turquoise
"#f1e157:#01edd2":35,\
#yellow (v3):medium purple
"#f1e157:#c66aff":75,\
#yellow (v3):light electric pink (v1)
"#f1e157:#eb61ff":45,\
#yellow (v3):light electric pink (v2)
"#f1e157:#fc90ff":30,\
#yellow (v3):electric pink
"#f1e157:#f574ff":30,\
#yellow (v3):dark electric pink
"#f1e157:#ff60e1":40,\
#yellow (v3):coral
"#f1e157:#f88379":20,\
#yellow (v3):purple (v1)
"#f1e157:#977aff":30,\
#yellow (v3):purple (v2)
"#f1e157:#a971fc":35,\
#yellow (v3):purple (v3)
"#f1e157:#b76eff":40,\
#yellow (v3):purple (v4)
"#f1e157:#d985f7":35,\
#yellow (v3):purple (v5)
"#f1e157:#7f5fff":35,\
#yellow (v3):purple (v6)
"#f1e157:#a991ff":30,\
#yellow (v3):purple (v7)
"#f1e157:#a293ff":40,\
#yellow (v3):pink (v2)
"#f1e157:#ff7d9c":30,\
#yellow (v3):pink (v3)
"#f1e157:#fc98bc":15,\
#yellow (v3):reddish (v1)
"#f1e157:#ff5f5f":30,\
#yellow (v3):reddish (v2)
"#f1e157:#ff5a5a":30,\
#yellow (v3):tomato
"#f1e157:#ff8282":25,\
#yellow (v3):greenish yellow
"#f1e157:#d4d900":1,\
#yellow (v3):greenish
"#f1e157:#c8ff28":5,\
#yellow (v3):aquamarine (v1)
"#f1e157:#28ffaa":15,\
#yellow (v3):aquamarine (v2)
"#f1e157:#00eccb":25,\
#yellow (v3):firozi (v2)
"#f1e157:#2ff6ea":20,\
#yellow (v3):firozi (v3)
"#f1e157:#49d9ff":30,\
#yellow (v3):firozi (v4)
"#f1e157:#31e6ed":40,\
#yellow (v3):dull green
"#f1e157:#89e46c":15,\
#yellow (v3):mint greenish
"#f1e157:#9de245":7,\
#yellow (v3):mint green
"#f1e157:#66ff3a":15,\
#yellow (v3):light mint green
"#f1e157:#00f0a9":50,\
#yellow (v3):light green
"#f1e157:#a5ed31":10,\
#yellow (v3):green (v2)
"#f1e157:#2ff06f":20,\
#yellow (v3):green (v3)
"#f1e157:#26e99c":35,\
#yellow (v3):green (v4)
"#f1e157:#42ec72":20,\
#yellow (v3):green (v5)
"#f1e157:#46ec5c":20,\
#yellow (v3):green (v6)
"#f1e157:#50f777":20,\
#yellow (v3):green (v7)
"#f1e157:#01f5a1":25,\
#yellow (v3):green (v8)
"#f1e157:#42e966":20,\
#yellow (v3):green (v9)
"#f1e157:#52f578":20,\
#yellow (v3):sky blue (v1)
"#f1e157:#69baf5":45,\
#yellow (v3):sky blue (v2)
"#f1e157:#6d9eff":55,\
#yellow (v3):sky blue (v3)
"#f1e157:#32a8f8":40,\
#yellow (v3):sky blue (v4)
"#f1e157:#5caeff":25,\
#yellow (v3):sky blue (v5)
"#f1e157:#7ba6fc":35,\
#yellow (v3):blue
"#f1e157:#6292ff":45,\
#yellow (v3):sky-teal-blue
"#f1e157:#28d7ff":45,\
#yellow (v3):purple blue
"#f1e157:#9380ff":60,\
#yellow (v3):teal-blue (v1)
"#f1e157:#3bc1f0":50,\
#yellow (v3):teal-blue (v2)
"#f1e157:#34caf0":45,\
#yellow (v3):teal-blue (v3)
"#f1e157:#01b0ed":55,\
#yellow (v3):gold (v2)
"#f1e157:#f9cd48":1,\
#yellow (v3):gold (v3)
"#f1e157:#fed940":5,\
#yellow (v3):gold (v4)
"#f1e157:#ffd700":5,\
#yellow (v3):orange (v2)
"#f1e157:#ffaa5f":10,\
#yellow (v3):light orange
"#f1e157:#ffae7c":10,\
#yellow (v3):yellow-orange
"#f1e157:#ffca5f":1,\
#yellow (v3):yellow (v1)
"#f1e157:#fff03a":5,\
#yellow (v3):yellow (v2)
"#f1e157:#ebdf59":1,\
#yellow (v3):yellow (v3)
"#f1e157:#f1e157":0,\
#yellow (v3):pink orange
"#f1e157:#ff9a84":15,\
#yellow (v3):indigo (v1)
"#f1e157:#c97fff":45,\
#yellow (v3):indigo (v2)
"#f1e157:#6e76ff":60,\

#pink orange:turquoise
"#ff9a84:#01edd2":55,\
#pink orange:medium purple
"#ff9a84:#c66aff":35,\
#pink orange:light electric pink (v1)
"#ff9a84:#eb61ff":25,\
#pink orange:light electric pink (v2)
"#ff9a84:#fc90ff":15,\
#pink orange:electric pink
"#ff9a84:#f574ff":15,\
#pink orange:dark electric pink
"#ff9a84:#ff60e1":15,\
#pink orange:coral
"#ff9a84:#f88379":1,\
#pink orange:purple (v1)
"#ff9a84:#977aff":45,\
#pink orange:purple (v2)
"#ff9a84:#a971fc":45,\
#pink orange:purple (v3)
"#ff9a84:#b76eff":35,\
#pink orange:purple (v4)
"#ff9a84:#d985f7":20,\
#pink orange:purple (v5)
"#ff9a84:#7f5fff":60,\
#pink orange:purple (v6)
"#ff9a84:#a991ff":25,\
#pink orange:purple (v7)
"#ff9a84:#a293ff":45,\
#pink orange:pink (v2)
"#ff9a84:#ff7d9c":5,\
#pink orange:pink (v3)
"#ff9a84:#fc98bc":5,\
#pink orange:reddish (v1)
"#ff9a84:#ff5f5f":5,\
#pink orange:reddish (v2)
"#ff9a84:#ff5a5a":7,\
#pink orange:tomato
"#ff9a84:#ff8282":1,\
#pink orange:greenish yellow
"#ff9a84:#d4d900":20,\
#pink orange:greenish
"#ff9a84:#c8ff28":30,\
#pink orange:aquamarine (v1)
"#ff9a84:#28ffaa":40,\
#pink orange:aquamarine (v2)
"#ff9a84:#00eccb":30,\
#pink orange:firozi (v2)
"#ff9a84:#2ff6ea":35,\
#pink orange:firozi (v3)
"#ff9a84:#49d9ff":35,\
#pink orange:firozi (v4)
"#ff9a84:#31e6ed":40,\
#pink orange:dull green
"#ff9a84:#89e46c":35,\
#pink orange:mint greenish
"#ff9a84:#9de245":25,\
#pink orange:mint green
"#ff9a84:#66ff3a":30,\
#pink orange:light mint green
"#ff9a84:#00f0a9":45,\
#pink orange:light green
"#ff9a84:#a5ed31":25,\
#pink orange:green (v2)
"#ff9a84:#2ff06f":35,\
#pink orange:green (v3)
"#ff9a84:#26e99c":40,\
#pink orange:green (v4)
"#ff9a84:#42ec72":35,\
#pink orange:green (v5)
"#ff9a84:#46ec5c":45,\
#pink orange:green (v6)
"#ff9a84:#50f777":30,\
#pink orange:green (v7)
"#ff9a84:#01f5a1":35,\
#pink orange:green (v8)
"#ff9a84:#42e966":35,\
#pink orange:green (v9)
"#ff9a84:#52f578":35,\
#pink orange:sky blue (v1)
"#ff9a84:#69baf5":40,\
#pink orange:sky blue (v2)
"#ff9a84:#6d9eff":35,\
#pink orange:sky blue (v3)
"#ff9a84:#32a8f8":35,\
#pink orange:sky blue (v4)
"#ff9a84:#5caeff":35,\
#pink orange:sky blue (v5)
"#ff9a84:#7ba6fc":40,\
#pink orange:blue
"#ff9a84:#6292ff":40,\
#pink orange:sky-teal-blue
"#ff9a84:#28d7ff":40,\
#pink orange:purple blue
"#ff9a84:#9380ff":30,\
#pink orange:teal-blue (v1)
"#ff9a84:#3bc1f0":35,\
#pink orange:teal-blue (v2)
"#ff9a84:#34caf0":40,\
#pink orange:teal-blue (v3)
"#ff9a84:#01b0ed":45,\
#pink orange:gold (v2)
"#ff9a84:#f9cd48":10,\
#pink orange:gold (v3)
"#ff9a84:#fed940":20,\
#pink orange:gold (v4)
"#ff9a84:#ffd700":10,\
#pink orange:orange (v2)
"#ff9a84:#ffaa5f":5,\
#pink orange:light orange
"#ff9a84:#ffae7c":1,\
#pink orange:yellow-orange
"#ff9a84:#ffca5f":15,\
#pink orange:yellow (v1)
"#ff9a84:#fff03a":15,\
#pink orange:yellow (v2)
"#ff9a84:#ebdf59":15,\
#pink orange:yellow (v3)
"#ff9a84:#f1e157":15,\
#pink orange:pink orange
"#ff9a84:#ff9a84":0,\
#pink orange:indigo (v1)
"#ff9a84:#c97fff":20,\
#pink orange:indigo (v2)
"#ff9a84:#6e76ff":40,\

#indigo (v1):turquoise
"#c97fff:#01edd2":70,\
#indigo (v1):medium purple
"#c97fff:#c66aff":1,\
#indigo (v1):light electric pink (v1)
"#c97fff:#eb61ff":5,\
#indigo (v1):light electric pink (v2)
"#c97fff:#fc90ff":5,\
#indigo (v1):electric pink
"#c97fff:#f574ff":5,\
#indigo (v1):dark electric pink
"#c97fff:#ff60e1":7,\
#indigo (v1):coral
"#c97fff:#f88379":30,\
#indigo (v1):purple (v1)
"#c97fff:#977aff":5,\
#indigo (v1):purple (v2)
"#c97fff:#a971fc":5,\
#indigo (v1):purple (v3)
"#c97fff:#b76eff":1,\
#indigo (v1):purple (v4)
"#c97fff:#d985f7":1,\
#indigo (v1):purple (v5)
"#c97fff:#7f5fff":15,\
#indigo (v1):purple (v6)
"#c97fff:#a991ff":5,\
#indigo (v1):purple (v7)
"#c97fff:#a293ff":5,\
#indigo (v1):pink (v2)
"#c97fff:#ff7d9c":30,\
#indigo (v1):pink (v3)
"#c97fff:#fc98bc":20,\
#indigo (v1):reddish (v1)
"#c97fff:#ff5f5f":35,\
#indigo (v1):reddish (v2)
"#c97fff:#ff5a5a":30,\
#indigo (v1):tomato
"#c97fff:#ff8282":40,\
#indigo (v1):greenish yellow
"#c97fff:#d4d900":40,\
#indigo (v1):greenish
"#c97fff:#c8ff28":45,\
#indigo (v1):aquamarine (v1)
"#c97fff:#28ffaa":45,\
#indigo (v1):aquamarine (v2)
"#c97fff:#00eccb":45,\
#indigo (v1):firozi (v2)
"#c97fff:#2ff6ea":35,\
#indigo (v1):firozi (v3)
"#c97fff:#49d9ff":20,\
#indigo (v1):firozi (v4)
"#c97fff:#31e6ed":50,\
#indigo (v1):dull green
"#c97fff:#89e46c":55,\
#indigo (v1):mint greenish
"#c97fff:#9de245":45,\
#indigo (v1):mint green
"#c97fff:#66ff3a":50,\
#indigo (v1):light mint green
"#c97fff:#00f0a9":55,\
#indigo (v1):light green
"#c97fff:#a5ed31":45,\
#indigo (v1):green (v2)
"#c97fff:#2ff06f":45,\
#indigo (v1):green (v3)
"#c97fff:#26e99c":50,\
#indigo (v1):green (v4)
"#c97fff:#42ec72":55,\
#indigo (v1):green (v5)
"#c97fff:#46ec5c":55,\
#indigo (v1):green (v6)
"#c97fff:#50f777":45,\
#indigo (v1):green (v7)
"#c97fff:#01f5a1":60,\
#indigo (v1):green (v8)
"#c97fff:#42e966":65,\
#indigo (v1):green (v9)
"#c97fff:#52f578":45,\
#indigo (v1):sky blue (v1)
"#c97fff:#69baf5":20,\
#indigo (v1):sky blue (v2)
"#c97fff:#6d9eff":15,\
#indigo (v1):sky blue (v3)
"#c97fff:#32a8f8":15,\
#indigo (v1):sky blue (v4)
"#c97fff:#5caeff":15,\
#indigo (v1):sky blue (v5)
"#c97fff:#7ba6fc":20,\
#indigo (v1):blue
"#c97fff:#6292ff":20,\
#indigo (v1):sky-teal-blue
"#c97fff:#28d7ff":20,\
#indigo (v1):purple blue
"#c97fff:#9380ff":10,\
#indigo (v1):teal-blue (v1)
"#c97fff:#3bc1f0":25,\
#indigo (v1):teal-blue (v2)
"#c97fff:#34caf0":25,\
#indigo (v1):teal-blue (v3)
"#c97fff:#01b0ed":15,\
#indigo (v1):gold (v2)
"#c97fff:#f9cd48":45,\
#indigo (v1):gold (v3)
"#c97fff:#fed940":55,\
#indigo (v1):gold (v4)
"#c97fff:#ffd700":65,\
#indigo (v1):orange (v2)
"#c97fff:#ffaa5f":45,\
#indigo (v1):light orange
"#c97fff:#ffae7c":35,\
#indigo (v1):yellow-orange
"#c97fff:#ffca5f":45,\
#indigo (v1):yellow (v1)
"#c97fff:#fff03a":30,\
#indigo (v1):yellow (v2)
"#c97fff:#ebdf59":40,\
#indigo (v1):yellow (v3)
"#c97fff:#f1e157":45,\
#indigo (v1):pink orange
"#c97fff:#ff9a84":20,\
#indigo (v1):indigo (v1)
"#c97fff:#c97fff":0,\
#indigo (v1):indigo (v2)
"#c97fff:#6e76ff":7,\

#indigo (v2):turquoise
"#c97fff:#01edd2":40,\
#indigo (v2):medium purple
"#c97fff:#c66aff":7,\
#indigo (v2):light electric pink (v1)
"#c97fff:#eb61ff":20,\
#indigo (v2):light electric pink (v2)
"#c97fff:#fc90ff":25,\
#indigo (v2):electric pink
"#c97fff:#f574ff":10,\
#indigo (v2):dark electric pink
"#c97fff:#ff60e1":20,\
#indigo (v2):coral
"#c97fff:#f88379":45,\
#indigo (v2):purple (v1)
"#c97fff:#977aff":1,\
#indigo (v2):purple (v2)
"#c97fff:#a971fc":5,\
#indigo (v2):purple (v3)
"#c97fff:#b76eff":10,\
#indigo (v2):purple (v4)
"#c97fff:#d985f7":15,\
#indigo (v2):purple (v5)
"#c97fff:#7f5fff":1,\
#indigo (v2):purple (v6)
"#c97fff:#a991ff":5,\
#indigo (v2):purple (v7)
"#c97fff:#a293ff":5,\
#indigo (v2):pink (v2)
"#c97fff:#ff7d9c":60,\
#indigo (v2):pink (v3)
"#c97fff:#fc98bc":50,\
#indigo (v2):reddish (v1)
"#c97fff:#ff5f5f":45,\
#indigo (v2):reddish (v2)
"#c97fff:#ff5a5a":60,\
#indigo (v2):tomato
"#c97fff:#ff8282":65,\
#indigo (v2):greenish yellow
"#c97fff:#d4d900":80,\
#indigo (v2):greenish
"#c97fff:#c8ff28":70,\
#indigo (v2):aquamarine (v1)
"#c97fff:#28ffaa":60,\
#indigo (v2):aquamarine (v2)
"#c97fff:#00eccb":55,\
#indigo (v2):firozi (v2)
"#c97fff:#2ff6ea":35,\
#indigo (v2):firozi (v3)
"#c97fff:#49d9ff":25,\
#indigo (v2):firozi (v4)
"#c97fff:#31e6ed":45,\
#indigo (v2):dull green
"#c97fff:#89e46c":65,\
#indigo (v2):mint greenish
"#c97fff:#9de245":50,\
#indigo (v2):mint green
"#c97fff:#66ff3a":70,\
#indigo (v2):light mint green
"#c97fff:#00f0a9":55,\
#indigo (v2):light green
"#c97fff:#a5ed31":55,\
#indigo (v2):green (v2)
"#c97fff:#2ff06f":60,\
#indigo (v2):green (v3)
"#c97fff:#26e99c":60,\
#indigo (v2):green (v4)
"#c97fff:#42ec72":75,\
#indigo (v2):green (v5)
"#c97fff:#46ec5c":75,\
#indigo (v2):green (v6)
"#c97fff:#50f777":65,\
#indigo (v2):green (v7)
"#c97fff:#01f5a1":80,\
#indigo (v2):green (v8)
"#c97fff:#42e966":70,\
#indigo (v2):green (v9)
"#c97fff:#52f578":65,\
#indigo (v2):sky blue (v1)
"#c97fff:#69baf5":5,\
#indigo (v2):sky blue (v2)
"#c97fff:#6d9eff":5,\
#indigo (v2):sky blue (v3)
"#c97fff:#32a8f8":5,\
#indigo (v2):sky blue (v4)
"#c97fff:#5caeff":7,\
#indigo (v2):sky blue (v5)
"#c97fff:#7ba6fc":5,\
#indigo (v2):blue
"#c97fff:#6292ff":5,\
#indigo (v2):sky-teal-blue
"#c97fff:#28d7ff":10,\
#indigo (v2):purple blue
"#c97fff:#9380ff":1,\
#indigo (v2):teal-blue (v1)
"#c97fff:#3bc1f0":5,\
#indigo (v2):teal-blue (v2)
"#c97fff:#34caf0":10,\
#indigo (v2):teal-blue (v3)
"#c97fff:#01b0ed":5,\
#indigo (v2):gold (v2)
"#c97fff:#f9cd48":70,\
#indigo (v2):gold (v3)
"#c97fff:#fed940":65,\
#indigo (v2):gold (v4)
"#c97fff:#ffd700":75,\
#indigo (v2):orange (v2)
"#c97fff:#ffaa5f":60,\
#indigo (v2):light orange
"#c97fff:#ffae7c":55,\
#indigo (v2):yellow-orange
"#c97fff:#ffca5f":65,\
#indigo (v2):yellow (v1)
"#c97fff:#fff03a":50,\
#indigo (v2):yellow (v2)
"#c97fff:#ebdf59":65,\
#indigo (v2):yellow (v3)
"#c97fff:#f1e157":60,\
#indigo (v2):pink orange
"#c97fff:#ff9a84":40,\
#indigo (v2):indigo (v1)
"#c97fff:#c97fff":7,\
#indigo (v2):indigo (v2)
"#c97fff:#6e76ff":0,\

}

# visual distance between various primary colors
PRIMARY_COLOR_DISTANCE = {\
#pink:pink
"#fa88a3:#fa88a3":0,\
#pink:dull pink
"#fa88a3:#e378ba":5,\
#pink:electric pink
"#fa88a3:#f574ff":10,\
#pink:turquoise
"#fa88a3:#01edd2":90,\
#pink:blue
"#fa88a3:#6292ff":80,\
#pink:green
"#fa88a3:#5cf48c":70,\
#pink:firozi
"#fa88a3:#2ed7e1":95,\
#pink:purle
"#fa88a3:#977aff":45,\
#pink:sky-teal-blue
"#fa88a3:#28d7ff":85,\
#pink:gold
"#fa88a3:#f4d140":35,\
#pink:coral
"#fa88a3:#f88379":5,\
#pink:medium purple
"#fa88a3:#c66aff":40,\
#pink:greenish yellow
"#fa88a3:#d4d900":40,\
#pink:orange
"#fa88a3:#ffbe69":15,\
#pink:light mint green
"#fa88a3:#00f0a9":85,\

#dull pink:pink
"#e378ba:#fa88a3":5,\
#dull pink:dull pink
"#e378ba:#e378ba":0,\
#dull pink:electric pink
"#e378ba:#f574ff":5,\
#dull pink:turquoise
"#e378ba:#01edd2":90,\
#dull pink:blue
"#e378ba:#6292ff":70,\
#dull pink:green
"#e378ba:#5cf48c":75,\
#dull pink:firozi
"#e378ba:#2ed7e1":85,\
#dull pink:purple
"#e378ba:#977aff":25,\
#dull pink:sky-teal-blue
"#e378ba:#28d7ff":85,\
#dull pink:gold
"#e378ba:#f4d140":45,\
#dull pink:coral
"#e378ba:#f88379":10,\
#dull pink:medium purple
"#e378ba:#c66aff":15,\
#dull pink:greenish yellow
"#e378ba:#d4d900":70,\
#dull pink:orange
"#e378ba:#ffbe69":35,\
#dull pink:light mint green
"#e378ba:#00f0a9":85,\

#electric pink:pink
"#f574ff:#fa88a3":10,\
#electric pink:dull pink
"#f574ff:#e378ba":5,\
#electric pink:electric pink
"#f574ff:#f574ff":0,\
#electric pink:turquoise
"#f574ff:#01edd2":80,\
#electric pink:blue
"#f574ff:#6292ff":45,\
#electric pink:green
"#f574ff:#5cf48c":65,\
#electric pink:firozi
"#f574ff:#2ed7e1":70,\
#electric pink:purple
"#f574ff:#977aff":10,\
#electric pink:sky-teal-blue
"#f574ff:#28d7ff":75,\
#electric pink:gold
"#f574ff:#f4d140":60,\
#electric pink:coral
"#f574ff:#f88379":25,\
#electric pink:medium purple
"#f574ff:#c66aff":5,\
#electric pink:greenish yellow
"#f574ff:#d4d900":65,\
#electric pink:orange
"#f574ff:#ffbe69":35,\
#electric pink:light mint green
"#f574ff:#00f0a9":70,\

#turquoise:pink
"#01edd2:#fa88a3":90,\
#turquoise:dull punk
"#01edd2:#e378ba":90,\
#turquoise:electric pink
"#01edd2:#f574ff":80,\
#turquoise:turquoise
"#01edd2:#01edd2":0,\
#turquoise:blue
"#01edd2:#6292ff":40,\
#turquoise:green
"#01edd2:#5cf48c":20,\
#turquoise:firozi
"#01edd2:#2ed7e1":5,\
#turquoise:purple
"#01edd2:#977aff":55,\
#turquoise:sky-teal-blue
"#01edd2:#28d7ff":15,\
#turquoise:gold
"#01edd2:#f4d140":35,\
#turquoise:coral
"#01edd2:#f88379":45,\
#turquoise:medium purple
"#01edd2:#c66aff":35,\
#turquoise:greenish yellow
"#01edd2:#d4d900":20,\
#turquoise:orange
"#01edd2:#ffbe69":35,\
#turquoise:light mint green
"#01edd2:#00f0a9":5,\

#blue:pink
"#6292ff:#fa88a3":80,\
#blue:dull pink
"#6292ff:#e378ba":70,\
#blue:electric pink
"#6292ff:#f574ff":45,\
#blue:turquoise
"#6292ff:#01edd2":40,\
#blue:blue
"#6292ff:#6292ff":0,\
#blue:green
"#6292ff:#5cf48c":60,\
#blue:firozi
"#6292ff:#2ed7e1":10,\
#blue:purple
"#6292ff:#977aff":10,\
#blue:sky-teal-blue
"#6292ff:#28d7ff":10,\
#blue:gold
"#6292ff:#f4d140":65,\
#blue:coral
"#6292ff:#f88379":65,\
#blue:medium purple
"#6292ff:#c66aff":10,\
#blue:greenish yellow
"#6292ff:#d4d900":80,\
#blue:orange
"#6292ff:#ffbe69":60,\
#blue:light mint green
"#6292ff:#00f0a9":35,\

#green:pink
"#5cf48c:#fa88a3":70,\
#green:dull pink
"#5cf48c:#e378ba":75,\
#green:electric pink
"#5cf48c:#f574ff":65,\
#green:turquoise
"#5cf48c:#01edd2":20,\
#green:blue
"#5cf48c:#6292ff":60,\
#green:green
"#5cf48c:#5cf48c":0,\
#green:firozi
"#5cf48c:#2ed7e1":30,\
#green:purple
"#5cf48c:#977aff":60,\
#green:sky-teal-blue
"#5cf48c:#28d7ff":35,\
#green:gold
"#5cf48c:#f4d140":50,\
#green:coral
"#5cf48c:#f88379":60,\
#green:medium purple
"#5cf48c:#c66aff":70,\
#green:greenish yellow
"#5cf48c:#d4d900":35,\
#green:orange
"#5cf48c:#ffbe69":35,\
#green:light mint green
"#5cf48c:#00f0a9":5,\

#firozi:pink
"#2ed7e1:#fa88a3":95,\
#firozi:dull pink
"#2ed7e1:#e378ba":85,\
#firozi:electric pink
"#2ed7e1:#f574ff":70,\
#firozi:turquoise
"#2ed7e1:#01edd2":5,\
#firozi:blue
"#2ed7e1:#6292ff":10,\
#firozi:green
"#2ed7e1:#5cf48c":30,\
#firozi:firozi
"#2ed7e1:#2ed7e1":0,\
#firozi:purple
"#2ed7e1:#977aff":20,\
#firozi:sky-teal-blue
"#2ed7e1:#28d7ff":5,\
#firozi:gold
"#2ed7e1:#f4d140":50,\
#firozi:coral
"#2ed7e1:#f88379":75,\
#firozi:medium purple
"#2ed7e1:#c66aff":30,\
#firozi:greenish yellow
"#2ed7e1:#d4d900":35,\
#firozi:orange
"#2ed7e1:#ffbe69":55,\
#firozi:light mint green
"#2ed7e1:#00f0a9":20,\

#purple:pink
"#977aff:#fa88a3":45,\
#purple:dull pink
"#977aff:#e378ba":25,\
#purple:electric pink
"#977aff:#f574ff":10,\
#purple:turquoise
"#977aff:#01edd2":55,\
#purple:blue
"#977aff:#6292ff":10,\
#purple:green
"#977aff:#5cf48c":60,\
#purple:firozi
"#977aff:#2ed7e1":20,\
#purple:purple
"#977aff:#977aff":0,\
#purple:sky-teal-blue
"#977aff:#28d7ff":10,\
#purple:gold
"#977aff:#f4d140":70,\
#purple:coral
"#977aff:#f88379":40,\
#purple:medium purple
"#977aff:#c66aff":5,\
#purple:greenish yellow
"#977aff:#d4d900":65,\
#purple:orange
"#977aff:#ffbe69":60,\
#purple:light mint green
"#977aff:#00f0a9":30,\

#sky-teal-blue:pink
"#28d7ff:#fa88a3":85,\
#sky-teal-blue:dull pink
"#28d7ff:#e378ba":85,\
#sky-teal-blue:electric pink
"#28d7ff:#f574ff":75,\
#sky-teal-blue:turquoise
"#28d7ff:#01edd2":15,\
#sky-teal-blue:blue
"#28d7ff:#6292ff":10,\
#sky-teal-blue:green
"#28d7ff:#5cf48c":35,\
#sky-teal-blue:firozi
"#28d7ff:#2ed7e1":5,\
#sky-teal-blue:purple
"#28d7ff:#977aff":10,\
#sky-teal-blue:sky-teal-blue
"#28d7ff:#28d7ff":0,\
#sky-teal-blue:gold
"#28d7ff:#f4d140":75,\
#sky-teal-blue:coral
"#28d7ff:#f88379":60,\
#sky-teal-blue:medium purple
"#28d7ff:#c66aff":20,\
#sky-teal-blue:greenish yellow
"#28d7ff:#d4d900":65,\
#sky-teal-blue:orange
"#28d7ff:#ffbe69":55,\
#sky-teal-blue:light mint green
"#28d7ff:#00f0a9":30,\

#gold:pink
"#f4d140:#fa88a3":35,\
#gold:dull pink
"#f4d140:#e378ba":45,\
#gold:electric pink
"#f4d140:#f574ff":60,\
#gold:turquoise
"#f4d140:#01edd2":35,\
#gold:blue
"#f4d140:#6292ff":65,\
#gold:green
"#f4d140:#5cf48c":50,\
#gold:firozi
"#f4d140:#2ed7e1":50,\
#gold:purple
"#f4d140:#977aff":70,\
#gold:sky-teal-blue
"#f4d140:#28d7ff":75,\
#gold:gold
"#f4d140:#f4d140":0,\
#gold:coral
"#f4d140:#f88379":55,\
#gold:medium purple
"#f4d140:#c66aff":75,\
#gold:greenish yellow
"#f4d140:#d4d900":5,\
#gold:orange
"#f4d140:#ffbe69":5,\
#gold:light mint green
"#f4d140:#00f0a9":40,\

#coral:pink
"#f88379:#fa88a3":5,\
#coral:dull pink
"#f88379:#e378ba":10,\
#coral:electric pink
"#f88379:#f574ff":25,\
#coral:turquoise
"#f88379:#01edd2":45,\
#coral:blue
"#f88379:#6292ff":65,\
#coral:green
"#f88379:#5cf48c":60,\
#coral:firozi
"#f88379:#2ed7e1":75,\
#coral:purple
"#f88379:#977aff":40,\
#coral:sky-teal-blue
"#f88379:#28d7ff":60,\
#coral:gold
"#f88379:#f4d140":55,\
#coral:coral
"#f88379:#f88379":0,\
#coral:medium purple
"#f88379:#c66aff":20,\
#coral:greenish yellow
"#f88379:#d4d900":25,\
#coral:orange
"#f88379:#ffbe69":10,\
#coral:light mint green
"#f88379:#00f0a9":70,\

#medium purple:pink
"#c66aff:#fa88a3":40,\
#medium purple:dull pink
"#c66aff:#e378ba":15,\
#medium purple:electric pink
"#c66aff:#f574ff":5,\
#medium purple:turquoise
"#c66aff:#01edd2":35,\
#medium purple:blue
"#c66aff:#6292ff":10,\
#medium purple:green
"#c66aff:#5cf48c":70,\
#medium purple:firozi
"#c66aff:#2ed7e1":30,\
#medium purple:purple
"#c66aff:#977aff":5,\
#medium purple:sky-teal-blue
"#c66aff:#28d7ff":20,\
#medium purple:gold
"#c66aff:#f4d140":75,\
#medium purple:coral
"#c66aff:#f88379":20,\
#medium purple:medium purple
"#c66aff:#c66aff":0,\
#medium purple:greenish yellow
"#c66aff:#d4d900":75,\
#medium purple:orange
"#c66aff:#ffbe69":40,\
#medium purple:light mint green
"#c66aff:#00f0a9":60,\

#greenish yellow:pink
"#d4d900:#fa88a3":40,\
#greenish yellow:dull pink
"#d4d900:#e378ba":70,\
#greenish yellow:electric pink
"#d4d900:#f574ff":65,\
#greenish yellow:turquoise
"#d4d900:#01edd2":20,\
#greenish yellow:blue
"#d4d900:#6292ff":80,\
#greenish yellow:green
"#d4d900:#5cf48c":35,\
#greenish yellow:firozi
"#d4d900:#2ed7e1":35,\
#greenish yellow:purple
"#d4d900:#977aff":65,\
#greenish yellow:sky-teal-blue
"#d4d900:#28d7ff":65,\
#greenish yellow:gold
"#d4d900:#f4d140":5,\
#greenish yellow:coral
"#d4d900:#f88379":25,\
#greenish yellow:medium purple
"#d4d900:#c66aff":75,\
#greenish yellow:greenish yellow
"#d4d900:#d4d900":0,\
#greenish yellow:orange
"#d4d900:#ffbe69":10,\
#greenish yellow:light mint green
"#d4d900:#00f0a9":25,\

#orange:pink
"#ffbe69:#fa88a3":15,\
#orange:dull pink
"#ffbe69:#e378ba":35,\
#orange:electric pink
"#ffbe69:#f574ff":35,\
#orange:turquoise
"#ffbe69:#01edd2":35,\
#orange:blue
"#ffbe69:#6292ff":60,\
#orange:green
"#ffbe69:#5cf48c":35,\
#orange:firozi
"#ffbe69:#2ed7e1":55,\
#orange:purple
"#ffbe69:#977aff":60,\
#orange:sky-teal-blue
"#ffbe69:#28d7ff":55,\
#orange:gold
"#ffbe69:#f4d140":5,\
#orange:coral
"#ffbe69:#f88379":10,\
#orange:medium purple
"#ffbe69:#c66aff":40,\
#orange:greenish yellow
"#ffbe69:#d4d900":10,\
#orange:orange
"#ffbe69:#ffbe69":0,\
#orange:light mint green
"#ffbe69:#00f0a9":70,\

#light mint green:pink
"#00f0a9:#fa88a3":85,\
#light mint green:dull pink
"#00f0a9:#e378ba":80,\
#light mint green:electric pink
"#00f0a9:#f574ff":70,\
#light mint green:turquoise
"#00f0a9:#01edd2":5,\
#light mint green:blue
"#00f0a9:#6292ff":35,\
#light mint green:green
"#00f0a9:#5cf48c":5,\
#light mint green:firozi
"#00f0a9:#2ed7e1":20,\
#light mint green:purple
"#00f0a9:#977aff":30,\
#light mint green:sky-teal-blue
"#00f0a9:#28d7ff":30,\
#light mint green:gold
"#00f0a9:#f4d140":40,\
#light mint green:coral
"#00f0a9:#f88379":70,\
#light mint green:medium purple
"#00f0a9:#c66aff":60,\
#light mint green:greenish yellow
"#00f0a9:#d4d900":25,\
#light mint green:orange
"#00f0a9:#ffbe69":70,\
#light mint green:light mint green:
"#00f0a9:#00f0a9":0}

COLOR_GRADIENTS = {\
#electric pink, sky-teal-blue
'1a':("#f574ff","#28d7ff"),\
#electric pink, purple
'1b':('#f574ff','#977aff'),\
#electric pink, pink 
'1c':("#f574ff","#ff7d9c"),\
#electric pink, yellow-orange
'1d':("#f574ff","#ffca5f"),\
#electric pink, reddish
'1e':("#f574ff","#ff5f5f"),\
#electric pink, greenish
'1f':("#f574ff","#c8ff28"),\
#electric pink, aquamarine
'1g':("#f574ff","#28ffaa"),\
#electric pink, firozi
'1h':("#f574ff","#2ff6ea"),\

#turquoise, purple
'2a':("#01edd2","#a971fc"),\
#turquoise, mint greenish
'2b':("#01edd2","#9de245"),\
#turquoise, green
'2c':("#01edd2","#2ff06f"),\
#turquoise, sky blue
'2d':("#01edd2","#69baf5"),\
#turquoise, gold
'2e':("#01edd2","#f9cd48"),\
#turquoise, firozi
'2f':("#01edd2","#49d9ff"),\
#turquoise, orange
'2g':("#01edd2","#ffaa5f"),\
#turquoise, blue
'2h':("#01edd2","#6292ff"),\

#blue, mint-green
'3a':("#6292ff","#66ff3a"),\
#blue, electric pink
'3b':("#6292ff","#f574ff"),\
#blue, yellow
'3c':("#6292ff","#fff03a"),\
#blue, teal-blue
'3d':("#6292ff","#3bc1f0"),\
#blue, green
'3e':("#6292ff","#26e99c"),\
#blue, purple
'3f':("#6292ff","#b76eff"),\
#blue, aquamarine
'3g':("#6292ff","#00eccb"),\
#blue, reddish
'3h':("#6292ff","#ff5a5a"),\

#green, reddish
'4a':("#5cf48c","#ff5a5a"),\
#green, firozi
'4b':('#5cf48c','#31e6ed'),\
#green, sky blue
'4c':("#5cf48c","#6d9eff"),\
#green, turquoise
'4d':("#5cf48c","#01edd2"),\
#green, gold
'4e':("#5cf48c","#fed940"),\
#green, purple
'4f':("#5cf48c","#d985f7"),\
#green, light green
'4g':("#5cf48c","#a5ed31"),\
#green, teal-blue
'4h':("#5cf48c","#3bc1f0"),\

#firozi, electric pink
'5a':("#2ed7e1","#f574ff"),\
#firozi, dull green
'5b':("#2ed7e1","#89e46c"),\
#firozi, sky blue
'5c':("#2ed7e1","#32a8f8"),\
#firozi, purple
'5d':("#2ed7e1","#7f5fff"),\
#firozi, pink orange
'5e':("#2ed7e1","#ff9a84"),\
#firozi, pink
'5f':("#2ed7e1","#ff7d9c"),\
#firozi, greenish-yellow
'5g':("#2ed7e1","#d4d900"),\
#firozi, aquamarine
'5h':("#2ed7e1","#00eccb"),\

#purple, gold
'6a':("#977aff","#ffd700"),\
#purple, turquoise
'6b':("#977aff","#01edd2"),\
#purple, electric pink
'6c':("#977aff","#f574ff"),\
#purple, teal-blue
'6d':("#977aff","#3bc1f0"),\
#purple, green
'6e':("#977aff","#42ec72"),\
#purple, reddish
'6f':("#977aff","#ff5a5a"),\
#purple, light green
'6g':("#977aff","#a5ed31"),\
#purple, indigo
'6h':("#977aff","#c97fff"),\

#sky-teal-blue, light green
'7a':("#28d7ff","#a5ed31"),\
#sky-teal-blue, yellow
'7b':('#28d7ff','#ebdf59'),\
#sky-teal-blue, blue
'7c':('#28d7ff','#6292ff'),\
#sky-teal-blue, turquoise
'7d':('#28d7ff','#01edd2'),\
#sky-teal-blue, purple
'7e':('#28d7ff','#a991ff'),\
#sky-teal-blue, electric pink
'7f':('#28d7ff','#f574ff'),\
#sky-teal-blue, reddish
'7g':('#28d7ff','#ff5a5a'),\
#sky-teal-blue, green
'7h':('#28d7ff','#46ec5c'),\

#gold, turquoise
'8a':("#f4d140","#01edd2"),\
#gold, teal blue
'8b':('#f4d140','#3bc1f0'),\
#gold, purple
'8c':("#f4d140","#b76eff"),\
#gold, reddish
'8d':("#f4d140","#ff5a5a"),\
#gold, green
'8e':("#f4d140","#42e966"),\
#gold, purple
'8f':("#f4d140","#977aff"),\
#gold, light green
'8g':("#f4d140","#a5ed31"),\
#gold, sky blue
'8h':("#f4d140","#6d9eff"),\

#coral, blue
'9a':("#f88379","#6292ff"),\
#coral, light green
'9b':("#f88379","#a5ed31"),\
#coral, orange
'9c':("#f88379","#ffbe69"),\
#coral, electric pink
'9d':("#f88379","#f574ff"),\
#coral, turquoise
'9e':("#f88379","#01edd2"),\
#coral, purple
'9f':("#f88379","#a293ff"),\
#coral, pink
'9g':("#f88379","#fc98bc"),\
#coral, sky-teal-blue
'9h':("#f88379","#28d7ff"),\

#medium purple, teal-blue
'10a':("#c66aff","#34caf0"),\
#medium purple, dark electric pink
'10b':("#c66aff","#ff60e1"),\
#medium purple, green
'10c':("#c66aff","#50f777"),\

#greenish-yellow, coral
'11a':("#d4d900","#f88379"),\
#greenish-yellow, sky-teal-blue
'11b':("#d4d900","#28d7ff"),\
#greenish-yellow, green
'11c':("#d4d900","#01f5a1"),\

#orange, indigo
'12a':("#ffbe69","#6e76ff"),\
#orange, electric pink
'12b':("#ffbe69","#f574ff"),\
#orange, tomato
'12c':("#ffbe69","#ff8282"),\
#orange, turquoise
'12d':("#ffbe69","#01edd2"),\
#orange, teal-blue
'12e':("#ffbe69","#01b0ed"),\
#orange, green
'12f':("#ffbe69","#42e966"),\
#orange, purple
'12g':("#ffbe69","#b76eff"),\
#orange, pink
'12h':("#ffbe69","#ff7d9c"),\

#dull pink, yellow
'13a':("#e378ba","#f1e157"),\
#dull pink, sky blue
'13b':("#e378ba","#5caeff"),\
#dull pink, medium purple
'13c':("#e378ba","#c66aff"),\
#dull pink, green
'13d':("#e378ba","#52f578"),\
#dull pink, light mint green
'13e':("#e378ba","#00f0a9"),\
#dull pink, light electric pink
'13f':("#e378ba","#eb61ff"),\
#dull pink, light orange
'13g':("#e378ba","#ffae7c"),\
#dull pink, purple blue
'13h':("#e378ba","#9380ff"),\

#pink, indigo
'14a':("#fa88a3","#c97fff"),\
#pink, sky-blue
'14b':("#fa88a3","#7ba6fc"),\
#pink, yellow-orange
'14c':("#fa88a3","#ffca5f"),\


#light mint green, pink orange
'15a':("#00f0a9","#ff9a84"),\
#light mint green, purple
'15b':("#00f0a9","#977aff"),\
#light mint green, light electric pink
'15c':("#00f0a9","#fc90ff"),\
}

PRIMARY_COLOR_GRADIENT_MAPPING = {\
#turquoise
"#01edd2":['2a','2b','2c','2d','2e','2f','2g','2h'],\
#pink (v1)
"#fa88a3":['14a','14b','14c'],\
#dull pink
"#e378ba":['13a','13b','13c','13d','13e','13f','13g','13h'],\
#electric pink
"#f574ff":['1a','1b','1c','1d','1e','1f','1g','1h'],\
#blue
"#6292ff":['3a','3b','3c','3d','3e','3f','3g','3h'],\
#green (v1)
"#5cf48c":['4a','4b','4c','4d','4e','4f','4g','4h'],\
#firozi (v1)
"#2ed7e1":['5a','5b','5c','5d','5e','5f','5g','5h'],\
#purple (v1)
"#977aff":['6a','6b','6c','6d','6e','6f','6g','6h'],\
#sky-teal-blue
"#28d7ff":['7a','7b','7c','7d','7e','7f','7g','7h'],\
#gold (v1)
"#f4d140":['8a','8b','8c','8d','8e','8f','8g','8h'],\
#coral
"#f88379":['9a','9b','9c','9d','9e','9f','9g','9h'],\
#medium purple
"#c66aff":['10a','10b','10c'],\
#greenish yellow
"#d4d900":['11a','11b','11c'],\
#orange (v1)
"#ffbe69":['12a','12b','12c','12d','12e','12f','12g','12h'],\
#light mint green
"#00f0a9":['15a','15b','15c']	
}