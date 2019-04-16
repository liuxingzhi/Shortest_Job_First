import nltk
import re
from collections import Counter
from nltk.tag.perceptron import PerceptronTagger
import sys

reg_exp = '((A|N)+|((A|N)*(NP)?)(A|N)*)N'
p = re.compile(reg_exp)


def interpret_tag(tag):
    if tag.startswith("NN") and not(tag.endswith("S")):
        return "N"
    if tag.startswith("JJ"):
        return "A"
    if tag == "IN":
        return "P"
    else:
        return "_"


def get_tag_string(tags):
    return [interpret_tag(tag) for (tok, tag) in tags]


def get_all_terms_in_sent(reg_exp, sent):
    tokens = nltk.word_tokenize(sent)
    #tags = nltk.pos_tag(tokens)
    pretrain = PerceptronTagger()
    tags = pretrain.tag(tokens)
    tags = [[tag[0], tag[1]] for tag in tags]
    if(not(tags[0][1].startswith("NNP"))):
        tags[0][0] = tags[0][0].lower()
    tag_string = "".join(get_tag_string(tags))
    p = re.compile(reg_exp)
    res = []
    retrieved_phrases = p.finditer(tag_string)
    for m in retrieved_phrases:
        np_lst = [tok for (tok, tag) in tags[m.start(): m.start() + len(m.group())]]
        tag_lst = [interpret_tag(tag) for (tok, tag) in tags[m.start(): m.start() + len(m.group())]]
        res.append(" ".join(np_lst))
        if "P" in tag_lst:
            idx = tag_lst.index("P")
            res.append(" ".join(np_lst[:idx]))
            res.append(" ".join(np_lst[idx + 1:]))
    return res


def get_all_terms_in_doc(reg_exp, doc, min_freq=2):
    sents = nltk.sent_tokenize(doc)
    terms = []
    for sent in sents:
        terms += get_all_terms_in_sent(reg_exp, sent)
    term_cnt = Counter(terms)
    for term in term_cnt:
        if term_cnt[term] >= min_freq:
            yield term


if __name__ == '__main__':
    file_name = sys.argv[1]
    min_freq = int(sys.argv[2])
    out = sys.argv[3]

    with open(file_name, 'rb') as file:
        doc = file.read()
        doc = str(doc, "utf_8").encode('ascii', 'ignore').decode("ascii")
        terms = get_all_terms_in_doc(reg_exp, doc, min_freq)
        out_file = open(out, 'w')
        out_file.write("\n".join(list(terms)))
        out_file.close()
        file.close()
