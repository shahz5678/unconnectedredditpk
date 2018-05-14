# -*- coding: utf-8 -*-

# less intensive form of URL_REGEX3
URL_REGEX1 = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|aero|biz|cat|coop|info|int|jobs|mobi|museum|pro|tel|travel|ae|af|ai|al|am|ao|as|au|aw|ax|bd|bg|bh|bi|bm|bo|bs|bt|bw|ca|cd|cf|cg|ch|ci|ck|cm|cn|co|cr|cu|cv|cx|cy|cz|dd|dj|dk|dm|do|ec|eg|eh|er|es|et|eu|fi|fj|fk|fm|fr|ga|gb|gh|gl|gm|gn|gp|gs|gt|gu|gw|hk|hn|hr|ht|hu|id|ie|im|in|io|iq|is|je|jm|jo|jp|kg|kh|ki|kp|kr|kw|ky|kz|lb|lc|li|lk|lr|lt|lu|lv|ly|ma|mc|md|me|mg|ml|mm|mn|mo|mp|ms|mt|mv|mx|my|mz|na|nc|ne|nf|ni|nl|no|np|nu|nz|om|pe|pf|pg|ph|pk|pl|pn|pr|pt|qa|ru|rw|sc|sd|se|sg|sh|sj|sk|sl|sn|so|sr|ss|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|aero|biz|cat|coop|info|int|jobs|mobi|museum|pro|tel|travel|ae|af|al|ax|bg|bm|bo|bw|ca|cd|cf|cg|ci|ck|cm|cn|co|cu|cv|cx|cy|cz|dd|dj|dk|ec|eg|eh|er|et|eu|fi|fj|fk|fm|gb|gh|gl|gm|gn|gp|gs|gt|gu|gw|hk|ht|ie|im|in|io|iq|je|jm|jp|kg|kp|kw|kz|lb|lc|lk|lr|lt|lv|ly|mc|md|mg|ml|mo|mp|ms|mv|mx|mz|nc|nf|nl|np|nz|om|pf|pg|ph|pk|pl|pn|pt|qa|ru|rw|sd|sg|sh|sj|sk|sl|sn|sr|ss|sv|sx|sz|td|tf|tg|tj|tl|tn|tr|tt|tv|tz|ua|ug|uk|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|yt|yu|zm|zw)\b/?(?!@)))"""

# less intensive form of URL_REGEX3
URL_REGEX2 = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|ac|ad|ae|af|ag|al|an|aq|ar|at|ax|az|ba|bb|be|bf|bg|bj|bm|bn|bo|br|bv|bw|by|bz|ca|cc|cd|cf|cg|ci|ck|cl|cm|cn|co|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dz|ec|ee|eg|eh|er|et|eu|fi|fj|fk|fm|fo|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|ht|ie|il|im|in|io|iq|ir|it|je|jm|jp|ke|kg|km|kn|kp|kw|kz|la|lb|lc|lk|lr|ls|lt|lv|ly|mc|md|mg|mh|mk|ml|mo|mp|mq|mr|ms|mu|mv|mw|mx|mz|nc|nf|ng|nl|np|nr|nz|om|pa|pf|pg|ph|pk|pl|pm|pn|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sd|sg|sh|si|sj|Ja|sk|sl|sm|sn|sr|ss|st|su|sv|sx|sz|td|tf|tg|tj|tl|tn|tp|tr|tt|tv|tz|ua|ug|uk|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|yt|yu|zm|zw)\b/?(?!@)))"""

# this regex may be vulnerable to a denial of service attack if used on untrusted input with an NFA engine like Python's (https://en.wikipedia.org/wiki/ReDoS)
# for instance, it has pathetic performance for ".hehe.............................................................."
URL_REGEX3 = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

