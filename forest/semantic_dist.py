from nltk.corpus import wordnet as wn

def clean(word: str) -> str:
    return(word.replace('_', ' ').replace('-', ' '))

def get_synonyms(command: str) -> list:
    try:
        cmd = wn.morphy(command)
        variants = wn.synsets(cmd)
        children = sum([o.hyponyms() for o in variants], [])
        parents = sum([o.hypernyms() for o in variants], [])
        # siblings = sum([o.hyponyms() for o in parents], [])
        # cousins = sum([o.hyponyms() for o in siblings], [])
        relatives = sum([variants, children, parents], [])
        lemmas = sum([o.lemmas() for o in relatives], [])
        names = [clean(l.name()) for l in lemmas]
        examples = sum([o.examples() for o in relatives], [])
        definitions = [o.definition() for o in relatives]
        prompts = sum([names, examples, definitions], [])
        return(prompts)
    except:
        return([])

if __name__ == '__main__':
    print([(o, get_synonyms(clean(o))) for o in ['bot_challenge', 'echo', 'eval', 'goodbye', 'hello', 'help', 'ping', 'pong', 'printerfact', 'uptime']])